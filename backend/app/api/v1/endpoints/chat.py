from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import google.generativeai as genai

from app.core.config import settings
from app.core.database import get_db
from app.models.document import Document
from app.schemas.chat import ChatRequest, ChatResponse, ChatSource
from app.services.vector_service import query_vector_store

router = APIRouter()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)

@router.post("/", response_model=ChatResponse)
async def chat_with_swarm(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    POST endpoint that receives a natural language query, performs RAG context retrieval
    on ChromaDB, constructs a prompt for Gemini, and returns a grounded answer with citations.
    """
    query_text = request.query.strip()
    if not query_text:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # 1. Query ChromaDB for relevant document snippets
    hits = query_vector_store(query_text, limit=5)
    
    if not hits:
        return ChatResponse(
            answer="No relevant document snippets were found. Please ingest documents first to populate the knowledge base.",
            sources=[]
        )

    # 2. Extract context text
    context_snippets = []
    for hit in hits:
        context_snippets.append(f"Snippet: {hit['content']}")
    context_text = "\n\n".join(context_snippets)

    # 3. Generate Answer using Gemini
    system_prompt = (
        "You are an expert Enterprise Document Q&A Assistant. Your goal is to answer the user's question "
        "accurately based ONLY on the provided CONTEXT text. Do not make up facts. "
        "Keep your tone professional, objective, and structured. "
        "At the end of your answer, write a short sentence acknowledging the sources that helped you answer."
    )
    
    user_prompt = f"""
    CONTEXT:
    {context_text}
    
    USER QUESTION: {query_text}
    """

    answer_text = ""
    if not settings.GEMINI_API_KEY:
        answer_text = (
            f"[MOCK Grounded RAG Chat] You asked: '{query_text}'.\n"
            "This is a fallback response. Set GEMINI_API_KEY to see live RAG answers.\n"
            f"Retrieved Context Snippets matched: {len(hits)} occurrences."
        )
    else:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=system_prompt
            )
            response = model.generate_content(user_prompt)
            answer_text = response.text.strip()
        except Exception as e:
            print(f"[ERROR] Chat Gemini API failed: {e}")
            answer_text = f"Failed to retrieve response from AI service. (Error: {str(e)})"

    # 4. Resolve source document metadata from MySQL
    unique_doc_ids = list(set(hit["document_id"] for hit in hits))
    sources = []
    
    for doc_id in unique_doc_ids:
        result = await db.execute(
            select(Document.filename).where(Document.id == doc_id)
        )
        filename = result.scalar_one_or_none()
        if filename:
            sources.append(ChatSource(document_id=doc_id, filename=filename))

    return ChatResponse(answer=answer_text, sources=sources)

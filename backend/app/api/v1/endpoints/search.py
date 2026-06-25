from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.document import Document
from app.schemas.search import SearchResponse, SearchResultItem
from app.services.vector_service import query_vector_store

router = APIRouter()

@router.get("/", response_model=SearchResponse)
async def perform_search(
    q: str = Query(..., min_length=1, description="Natural language search query"),
    limit: int = Query(5, ge=1, le=20, description="Max search results to retrieve"),
    db: AsyncSession = Depends(get_db)
):
    """
    Performs RAG search on the document text vectors inside ChromaDB.
    Returns matched snippets along with details from MySQL.
    """
    # 1. Fetch hits from vector database
    hits = query_vector_store(q, limit=limit)
    
    # 2. Join documents by document_id in MySQL to find the file names
    results = []
    for hit in hits:
        doc_id = hit["document_id"]
        result = await db.execute(
            select(Document.filename).where(Document.id == doc_id)
        )
        filename = result.scalar_one_or_none() or "Unknown Document"
        
        results.append(
            SearchResultItem(
                id=hit["id"],
                document_id=doc_id,
                filename=filename,
                content=hit["content"],
                distance=hit["distance"]
            )
        )
        
    return SearchResponse(query=q, results=results)

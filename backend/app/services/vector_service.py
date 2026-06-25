import uuid
from typing import List, Dict, Any
import google.generativeai as genai
from app.core.config import settings
from app.core.vector_store import get_chroma_collection

# Configure Google Gemini SDK
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_embedding(text: str) -> List[float]:
    """
    Generates embedding for a single text snippet using text-embedding-004.
    """
    if not settings.GEMINI_API_KEY:
        # Fallback dummy embedding if API key is missing (for local testing/setup validation)
        return [0.0] * 768
        
    response = genai.embed_content(
        model="models/gemini-embedding-2-preview",
        content=text,
        task_type="retrieval_document"
    )
    return response['embedding']

def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """
    Generates embeddings for a batch of text snippets.
    """
    if not settings.GEMINI_API_KEY:
        # Fallback dummy embeddings if API key is missing
        return [[0.0] * 768 for _ in range(len(texts))]
        
    response = genai.embed_content(
        model="models/gemini-embedding-2-preview",
        content=texts,
        task_type="retrieval_document"
    )
    return response['embedding']

def index_document_chunks(document_id: str, chunks: List[str]) -> None:
    """
    Embeds and indexes document chunks in ChromaDB.
    """
    if not chunks:
        return
        
    embeddings = get_embeddings_batch(chunks)
    ids = [f"{document_id}_{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "chunk_index": i} for i in range(len(chunks))]
    
    collection = get_chroma_collection()
    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas
    )

def query_vector_store(query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Performs RAG search on ChromaDB.
    """
    if not settings.GEMINI_API_KEY:
        return []
        
    # Generate query embedding
    response = genai.embed_content(
        model="models/gemini-embedding-2-preview",
        content=query_text,
        task_type="retrieval_query"
    )
    query_embedding = response['embedding']
    
    collection = get_chroma_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=limit
    )
    
    hits = []
    if results and 'documents' in results and results['documents']:
        docs = results['documents'][0]
        metadatas = results['metadatas'][0]
        ids = results['ids'][0]
        distances = results['distances'][0] if 'distances' in results else [0.0] * len(docs)
        
        for i in range(len(docs)):
            hits.append({
                "id": ids[i],
                "document_id": metadatas[i]["document_id"],
                "content": docs[i],
                "distance": float(distances[i])
            })
    return hits

def delete_document_vectors(document_id: str) -> None:
    """
    Removes all chunks associated with a document_id from the vector index.
    """
    collection = get_chroma_collection()
    collection.delete(where={"document_id": document_id})

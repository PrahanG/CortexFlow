import chromadb
from app.core.config import settings

def get_chroma_client() -> chromadb.HttpClient:
    """
    Creates and returns an HTTP client connected to the dockerized ChromaDB or Chroma Cloud.
    """
    headers = {}
    if settings.CHROMA_API_KEY:
        headers["Authorization"] = f"Bearer {settings.CHROMA_API_KEY}"
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST, 
        port=settings.CHROMA_PORT,
        ssl=settings.CHROMA_SSL,
        headers=headers if headers else None
    )

def get_chroma_collection(client: chromadb.HttpClient = None):
    """
    Retrieves or creates the vector collection for DocuSwarm AI.
    """
    if client is None:
        client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME
    )

import chromadb
from app.core.config import settings

def get_chroma_client() -> chromadb.HttpClient:
    """
    Creates and returns an HTTP client connected to the dockerized ChromaDB.
    """
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST, 
        port=settings.CHROMA_PORT
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

import chromadb
from app.core.config import settings

def get_chroma_client():
    """
    Creates and returns a client connected to the dockerized ChromaDB or TryChroma Cloud.
    """
    if settings.CHROMA_API_KEY:
        return chromadb.CloudClient(
            api_key=settings.CHROMA_API_KEY,
            tenant=settings.CHROMA_TENANT,
            database=settings.CHROMA_DATABASE
        )
    return chromadb.HttpClient(
        host=settings.CHROMA_HOST, 
        port=settings.CHROMA_PORT,
        ssl=settings.CHROMA_SSL
    )

def get_chroma_collection(client = None):
    """
    Retrieves or creates the vector collection for DocuSwarm AI.
    """
    if client is None:
        client = get_chroma_client()
    return client.get_or_create_collection(
        name=settings.CHROMA_COLLECTION_NAME
    )

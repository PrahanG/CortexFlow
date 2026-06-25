import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "CortexFlow"
    API_V1_STR: str = "/api/v1"
    
    # Google Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # MySQL Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "mysql+aiomysql://docuswarm_user:docuswarm_password@localhost:3306/docuswarm_db"
    )
    
    # ChromaDB Configuration
    CHROMA_HOST: str = os.getenv("CHROMA_HOST", "localhost")
    CHROMA_PORT: int = int(os.getenv("CHROMA_PORT", 8000))
    CHROMA_COLLECTION_NAME: str = "documents"
    CHROMA_SSL: bool = os.getenv("CHROMA_SSL", "False").lower() in ("true", "1", "yes")
    CHROMA_API_KEY: str = os.getenv("CHROMA_API_KEY", "")
    CHROMA_TENANT: str = os.getenv("CHROMA_TENANT", "default_tenant")
    CHROMA_DATABASE: str = os.getenv("CHROMA_DATABASE", "default_database")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

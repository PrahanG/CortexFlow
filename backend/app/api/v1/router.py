from fastapi import APIRouter
from app.api.v1.endpoints import documents, search, stats, chat

api_router = APIRouter()

api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(stats.router, prefix="/stats", tags=["Dashboard Telemetry"])
api_router.include_router(chat.router, prefix="/chat", tags=["AI Swarm Chat"])

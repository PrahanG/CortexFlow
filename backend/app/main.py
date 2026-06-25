from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_models
from app.api.v1.router import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    try:
        await init_models()
        print("[DATABASE] Auto-migration complete. Tables initialized successfully.")
    except Exception as e:
        print(f"[DATABASE] Database connection or table creation failed: {e}")
    yield
    # Shutdown actions (if any)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS configuration
# Allow Angular frontend (typically http://localhost:4200) to query the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/api/v1/config")
def read_config():
    import os
    return {
        "ws_url": os.getenv("WS_URL", "ws://127.0.0.1:8080/api/v1/documents")
    }

@app.get("/")
def read_root():
    return {
        "status": "online",
        "project": settings.PROJECT_NAME,
        "message": "Welcome to the DocuSwarm AI Autonomous Governance & Triage API."
    }

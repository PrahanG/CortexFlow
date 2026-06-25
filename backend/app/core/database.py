from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

# Parse connection arguments for SSL
connect_args = {}
database_url = settings.DATABASE_URL

if "ssl=true" in database_url.lower():
    # Remove ssl=true from the URL so SQLAlchemy doesn't pass it as a string
    if "?" in database_url:
        base_url, query = database_url.split("?", 1)
        params = [p for p in query.split("&") if not p.lower().startswith("ssl=")]
        database_url = base_url + ("?" + "&".join(params) if params else "")
    # Pass custom ssl context to connect_args to bypass self-signed certificate validation
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

# Create async engine for MySQL
engine = create_async_engine(
    database_url, 
    echo=False, 
    pool_pre_ping=True,
    connect_args=connect_args
)

# Async session factory
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# SQLAlchemy 2.0 Base class
class Base(DeclarativeBase):
    pass

# FastAPI Dependency for DB sessions
async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# Initialize Database tables
async def init_models():
    # Import all models to ensure they are registered on Base
    import app.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


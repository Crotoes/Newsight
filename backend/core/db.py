from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, DateTime, func
from typing import AsyncGenerator
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Create base class for models first
Base = declarative_base()

# Base model with common fields
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Create async engine (will use SQLite for now if PostgreSQL is not available)
try:
    if settings.DATABASE_URL and "postgresql" in settings.DATABASE_URL:
        database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        # Fallback to SQLite
        database_url = "sqlite+aiosqlite:///./newsight.db"
        logger.warning("Using SQLite database as fallback")
    
    engine = create_async_engine(
        database_url,
        echo=True if settings.LOG_LEVEL == "DEBUG" else False,
        future=True
    )
except Exception as e:
    logger.error(f"Database engine creation failed: {e}")
    # Use in-memory SQLite as last resort
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )

# Create async session
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_db():
    """Initialize database tables"""
    try:
        async with engine.begin() as conn:
            # Import all models here to ensure they are registered
            try:
                from models.schemas import Article, Summary, User, VectorEmbedding
            except ImportError as e:
                logger.warning(f"Some models could not be imported: {e}")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        # Don't raise exception to allow app to start
        pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()
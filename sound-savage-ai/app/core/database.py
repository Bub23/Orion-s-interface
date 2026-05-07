"""
Database connection and ORM setup
SQLAlchemy 2.0 with async support
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, DateTime, func
from uuid import uuid4
from datetime import datetime
from app.core.config import settings

# Async engine
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,
    future=True
)

# Async session
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    future=True
)

# Base class for all models
Base = declarative_base()


class BaseModel(Base):
    """Base model with common fields"""
    __abstract__ = True

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


async def get_db():
    """Dependency for getting DB session"""
    async with async_session() as session:
        yield session

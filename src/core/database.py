from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    poolclass=NullPool,
    echo=settings.ENVIRONMENT == "development",
    connect_args={
        "ssl": "require"
    }
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

Base = declarative_base()

async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session


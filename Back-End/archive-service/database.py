from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from config import settings

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create declarative base
Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with async_session() as session:
        yield session
        await session.commit()

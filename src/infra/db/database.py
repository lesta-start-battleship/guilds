from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from settings import settings

engine = create_async_engine(str(settings.database_url), echo=True)


class Base(DeclarativeBase):
    pass


async def get_db():
    async_session_local = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with async_session_local() as session:
        yield session

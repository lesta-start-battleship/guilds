from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from settings import settings

engine = create_async_engine(str(settings.database_url), echo=True)


class Base(DeclarativeBase):
    pass

async_session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_session_maker()
    async with async_session as session:
        try:
            yield session
        finally:
            await session.close()
import asyncio

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from db.database import Base
import pytest_asyncio
from db.models.guild import Role, Guild, Member, GuildChatMessage

from settings import settings

SQLALCHEMY_DATABASE_URL = str(settings.database_url)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)
AsyncTestingSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def async_session():
    async with engine.connect() as conn:
        transaction = await conn.begin()
        session = AsyncSession(bind=conn, expire_on_commit=False)

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


@pytest.fixture(scope="module")
def test_db():
    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    return init_db

@pytest_asyncio.fixture(scope="function")
async def data_in(async_session):
    """Создаёт тестовые данные с использованием общей сессии."""
    role = Role(title="Tester")
    async_session.add(role)
    await async_session.commit()
    await async_session.refresh(role)

    guild = Guild(tag="test-tag", title="Test Guild", description="Test Desc", owner_id=2)
    async_session.add(guild)
    await async_session.commit()
    await async_session.refresh(guild)

    member = Member(
        user_id=42,
        user_name="Alice",
        guild_id=guild.id,
        guild_tag=guild.tag,
        role_id=role.id,
    )
    async_session.add(member)
    await async_session.commit()
    await async_session.refresh(member)

    return {
        "member": member
    }

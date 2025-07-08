import pytest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.guild import GuildChatMessage, Role, Guild, Member
import random
import string

def random_string(length=10):
    """Генерируем случайную строку для тэга."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

@pytest.mark.asyncio
async def test_models_crud(async_session):
    unique_tag = f"test-tag"

    role = Role(title="Tester")
    async_session.add(role)
    await async_session.commit()
    await async_session.refresh(role)

    guild = Guild(tag=unique_tag, title="Test Guild", description="Test Desc", owner_id=2)
    async_session.add(guild)
    await async_session.commit()
    await async_session.refresh(guild)

    member = Member(user_id=42, user_name="Alice", guild_id=guild.id, role_id=role.id)
    async_session.add(member)
    await async_session.commit()
    await async_session.refresh(member)

    msg = GuildChatMessage(guild_id=guild.id, user_id=member.user_id, content="Hello world!")
    async_session.add(msg)
    await async_session.commit()
    await async_session.refresh(msg)

    assert msg.content == "Hello world!"


import pytest
from db.models.guild import GuildChatMessage, Role, Guild, Member
import random
import string

def random_string(length=10):
    """генерируем строку для тэга"""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

@pytest.mark.asyncio
async def test_models_crud(async_session):
    # Generate unique tag for guild
    unique_tag = f"test-tag-{random_string(5)}"

    # Создаём роль
    role = Role(title=f"Tester")
    async_session.add(role)
    await async_session.commit()
    await async_session.refresh(role)

    # Создаём гильдию
    guild = Guild(tag=unique_tag, title="Test Guild", description="Test Desc", owner_id=1)
    async_session.add(guild)
    await async_session.commit()
    await async_session.refresh(guild)

    # Добавим участника
    member = Member(user_id=42, user_name="Alice", guild_id=guild.id, role_id=role.id)
    async_session.add(member)
    await async_session.commit()
    await async_session.refresh(member)

    # Сохраняем сообщение
    msg = GuildChatMessage(guild_id=guild.id, user_id=member.user_id, content="Hello world!")
    async_session.add(msg)
    await async_session.commit()
    await async_session.refresh(msg)

    # Проверяем
    assert guild.title == "Test Guild"
    assert member.user_name == "Alice"
    assert msg.content == "Hello world!"

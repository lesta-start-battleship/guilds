from sqlalchemy.ext.asyncio import AsyncSession
from db.models.guild import GuildChatMessage
from typing import Optional

class ChatRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_message(self, guild_id: int, user_id: int, content: str) -> GuildChatMessage:
        message = GuildChatMessage(
            guild_id=guild_id,
            user_id=user_id,
            content=content
        )
        self.session.add(message)
        await self.session.commit()
        return message

    async def get_messages(self, guild_id: int, limit: int = 100) -> list[GuildChatMessage]:
        # Реализация получения сообщений
        pass
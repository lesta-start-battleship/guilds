from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CreateChatRequestSchema(BaseModel):
    title: str


class CreateChatResponseSchema(BaseModel):
    oid: str
    title: str

    # fixme поправить
    # @classmethod
    # def from_entity(cls, chat: Chat) -> 'CreateChatResponseSchema':
    #     return CreateChatResponseSchema(
    #         oid=chat.oid,
    #         title=chat.title.as_generic_type(),
    #     )


class ErrorSchema(BaseModel):
    error: str




class WebSocketMessageSchema(BaseModel):
    chat_id: str
    sender_id: Optional[str] = None
    message: str
    timestamp: datetime = datetime.now()
    message_type: str = "text"  # Можно расширить для разных типов сообщений


from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class ChatMessageIn(BaseModel):
    chat_id: UUID
    user_id: UUID
    content: str

class ChatMessageOut(BaseModel):
    user_id: UUID
    content: str
    created_at: datetime

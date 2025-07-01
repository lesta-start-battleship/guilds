from pydantic import BaseModel, Field
from datetime import datetime
from db.models.guild_war import WarStatus

class DeclareWarRequest(BaseModel):
    initiator_guild_id: int = Field(..., description="ID гильдии, которая инициирует войну")
    target_guild_id: int = Field(..., description="ID гильдии, которой отправляется запрос на войну")

    initiator_owner_id: int = Field(..., description="ID владельца инициирующей гильдии (для проверки прав)")


class DeclareWarResponse(BaseModel):
    request_id: int = Field(..., description="ID заявки на войну")
    initiator_guild_id: int = Field(..., description="ID гильдии-инициатора")
    target_guild_id: int = Field(..., description="ID целевой гильдии")
    status: WarStatus = Field(..., description="Статус заявки")
    created_at: datetime = Field(..., description="Дата и время создания заявки")
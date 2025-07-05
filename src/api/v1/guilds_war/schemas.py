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


class ConfirmWarRequest(BaseModel):
    user_id: int = Field(..., description="ID пользователя, подтверждающего войну")

class ConfirmWarResponse(BaseModel):
    request_id: int
    initiator_guild_id: int
    target_guild_id: int
    status: WarStatus
    updated_at: datetime


class CancelWarRequest(BaseModel):
    user_id: int = Field(..., description="ID пользователя, пытающегося отменить")

class CancelWarResponse(BaseModel):
    request_id: int = Field(..., description="ID заявки на войну")
    status: WarStatus = Field(..., description="Статус заявки")
    cancelled_by: int = Field(..., description="ID пользователя, отменившего войну")
    cancelled_at: datetime
from pydantic import BaseModel, Field
from datetime import datetime
from db.models.guild_war import WarStatus
from typing import Literal, List, Optional
from fastapi import Query

class DeclareWarRequest(BaseModel):
    initiator_guild_id: int = Field(..., description="ID гильдии, которая инициирует войну")
    target_guild_id: int = Field(..., description="ID гильдии, которой отправляется запрос на войну")

    initiator_owner_id: int = Field(..., description="ID владельца инициирующей гильдии (для проверки прав)")

class DeclareWarResponse(BaseModel):
    war_id: int = Field(..., description="ID заявки на войну")
    initiator_guild_id: int = Field(..., description="ID гильдии-инициатора")
    target_guild_id: int = Field(..., description="ID целевой гильдии")
    status: WarStatus = Field(..., description="Статус заявки")
    created_at: datetime = Field(..., description="Дата и время создания заявки")

    
class DeclareWarMessage(BaseModel):
    war_id: int
    initiator_guild_id: int
    target_guild_id: int
    status: Literal[WarStatus.pending]
    created_at: datetime
    correlation_id: str

class ConfirmWarRequest(BaseModel):
    target_owner_id: int = Field(..., description="ID пользователя, подтверждающего войну")

class ConfirmWarMessage(BaseModel):
    war_id: int
    initiator_guild_id: int
    target_guild_id: int
    status: Literal[WarStatus.active]
    updated_at: datetime
    initiator_owner_id: int
    target_owner_id: int
    correlation_id: str

class ConfirmWarResponse(BaseModel):
    war_id: int
    initiator_guild_id: int
    target_guild_id: int
    status: WarStatus
    updated_at: datetime
    initiator_owner_id: int
    target_owner_id: int

class CancelWarRequest(BaseModel):
    owner_id: int = Field(..., description="ID пользователя, пытающегося отменить")

class CancelWarResponse(BaseModel):
    war_id: int = Field(..., description="ID заявки на войну")
    status: WarStatus = Field(..., description="Статус заявки")
    cancelled_by: int = Field(..., description="ID пользователя, отменившего войну")
    cancelled_at: datetime
    initiator_guild_id: int
    target_guild_id: int
    initiator_owner_id: int
    target_owner_id: int



class CancelWarMessage(BaseModel):
    war_id: int
    status: Literal[WarStatus.canceled]
    cancelled_by: int 
    cancelled_at: datetime
    initiator_guild_id: int
    target_guild_id: int
    initiator_owner_id: int
    target_owner_id: int
    correlation_id: str


class DeclinedWarMessage(BaseModel):
    war_id: int
    status: Literal[WarStatus.declined]
    initiator_guild_id: int
    target_guild_id: int
    initiator_owner_id: int
    target_owner_id: int
    declined_at: datetime
    correlation_id: str


class GuildWarItem(BaseModel):
    id: int
    initiator_guild_id: int
    target_guild_id: int
    status: WarStatus
    created_at: datetime

class GuildWarListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    results: List[GuildWarItem]


class GuildWarHistoryItem(BaseModel):
    id: int
    war_id: int
    initiator_guild_id: int
    target_guild_id: int
    status: WarStatus
    created_at: datetime
    finished_at: datetime


class GuildWarHistoryListResponse(BaseModel):
    page: int
    page_size: int
    total: int
    total_pages: int
    results: List[GuildWarHistoryItem]



class GuildWarListParams(BaseModel):
    user_id: int
    guild_id: int
    is_initiator: bool = False
    is_target: bool = False
    status: Optional[WarStatus] = None
    page: int = 1
    page_size: int = 20

    @classmethod
    def as_query_params(
        cls,
        user_id: int = Query(..., description="ID пользователя, участника гильдии"),
        guild_id: int = Query(..., description="ID гильдии"),
        is_initiator: bool = Query(False, description="Показать заявки, где гильдия инициатор"),
        is_target: bool = Query(False, description="Показать заявки, где гильдия цель"),
        status: Optional[WarStatus] = Query(None, description="Фильтр по статусу"),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
    ):
        return cls(
            user_id=user_id,
            guild_id=guild_id,
            is_initiator=is_initiator,
            is_target=is_target,
            status=status,
            page=page,
            page_size=page_size
        )
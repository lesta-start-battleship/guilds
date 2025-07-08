from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.guild_war import GuildWarRequest, GuildWarRequestHistory, WarStatus
from db.database import get_db
from .schemas import GuildWarItem, GuildWarHistoryItem
from typing import Union
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .utils import check_user_access

router = APIRouter()
http_bearer = HTTPBearer()

@router.get("/list/{war_id}", response_model=Union[GuildWarItem, GuildWarHistoryItem])
async def get_war_by_id(
    war_id: int = Path(..., description="ID войны"),
    session: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    
    payload = await check_user_access(token)
    print(payload)

    # 1. Ищем в активных (pending / active)
    result = await session.execute(
        select(GuildWarRequest).where(GuildWarRequest.id == war_id)
    )
    war = result.scalar_one_or_none()

    if war:
        return GuildWarItem(
            id=war.id,
            initiator_guild_id=war.initiator_guild_id,
            target_guild_id=war.target_guild_id,
            status=war.status,
            created_at=war.created_at
        )

    # 2. Ищем в истории (finished / canceled / declined / expired)
    result = await session.execute(
        select(GuildWarRequestHistory).where(GuildWarRequestHistory.war_id == war_id)
    )
    history = result.scalar_one_or_none()

    if history:
        return GuildWarHistoryItem(
            id=history.id,
            war_id=history.war_id,
            initiator_guild_id=history.initiator_guild_id,
            target_guild_id=history.target_guild_id,
            status=history.status,
            created_at=history.created_at,
            finished_at=history.finished_at
        )

    # 3. Не найдено нигде
    raise HTTPException(404, detail="War not found")
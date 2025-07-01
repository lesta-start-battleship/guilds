from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from db.models.guild import Guild
from db.models.guild_war import GuildWarRequest, WarStatus
from db.database import get_db

from .schemas import DeclareWarRequest, DeclareWarResponse

router = APIRouter()

@router.post("/declare", response_model=DeclareWarResponse)
async def declare_war(
    data: DeclareWarRequest,
    session: AsyncSession = Depends(get_db)
):
    # 1. Проверка, существует ли инициаторская гильдия
    result = await session.execute(
        select(Guild).where(Guild.id == data.initiator_guild_id)
    )
    initiator_guild = result.scalar_one_or_none()
    if not initiator_guild:
        raise HTTPException(status_code=404, detail="Initiator guild not found")

    # 2. Проверка, что пользователь — владелец этой гильдии
    if initiator_guild.owner_id != data.initiator_owner_id:
        raise HTTPException(status_code=403, detail="You are not the owner of this guild")

    # 3. Проверка, существует ли целевая гильдия
    result = await session.execute(
        select(Guild).where(Guild.id == data.target_guild_id)
    )
    target_guild = result.scalar_one_or_none()
    if not target_guild:
        raise HTTPException(status_code=404, detail="Target guild not found")

    # 4. Проверка: нет ли уже active/pending запроса между этими гильдиями
    result = await session.execute(
        select(GuildWarRequest).where(
            GuildWarRequest.initiator_guild_id == data.initiator_guild_id,
            GuildWarRequest.target_guild_id == data.target_guild_id,
            GuildWarRequest.status.in_([WarStatus.pending, WarStatus.active])
        )
    )
    existing_request = result.scalar_one_or_none()
    if existing_request:
        raise HTTPException(status_code=400, detail="War request already is pending or is active")

    # 5. Создание новой заявки
    new_request = GuildWarRequest(
        initiator_guild_id=data.initiator_guild_id,
        target_guild_id=data.target_guild_id,
        status=WarStatus.pending,
        created_at=datetime.now(timezone.utc)
    )
    session.add(new_request)
    await session.commit()
    await session.refresh(new_request)

    return DeclareWarResponse(
        request_id=new_request.id,
        initiator_guild_id=new_request.initiator_guild_id,
        target_guild_id=new_request.target_guild_id,
        status=new_request.status,
        created_at=new_request.created_at,
    )
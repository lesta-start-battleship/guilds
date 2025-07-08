from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Union
from db.database import get_db
from db.models.guild_war import GuildWarRequest, GuildWarRequestHistory, WarStatus
from db.models.guild import Member

from .schemas import GuildWarListResponse, GuildWarListParams, GuildWarHistoryListResponse, GuildWarItem, GuildWarHistoryItem

router = APIRouter()


@router.get("/list", response_model=Union[GuildWarListResponse, GuildWarHistoryListResponse])
async def list_guild_war_requests(
    params: GuildWarListParams = Depends(GuildWarListParams.as_query_params),
    session: AsyncSession = Depends(get_db),
):
    if params.is_initiator == params.is_target:
        raise HTTPException(400, detail="Укажите ровно один из параметров: is_initiator или is_target")

    # 🔒 Проверка, что user_id — участник указанной гильдии
    result = await session.execute(
        select(Member).where(
            Member.user_id == params.user_id,
            Member.guild_id == params.guild_id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(403, detail="User is not a member of the specified guild")

    # Выбор нужного поля
    if params.is_initiator:
        field_request = GuildWarRequest.initiator_guild_id
        field_history = GuildWarRequestHistory.initiator_guild_id
    else:
        field_request = GuildWarRequest.target_guild_id
        field_history = GuildWarRequestHistory.target_guild_id

    current_statuses = {WarStatus.pending, WarStatus.active}
    history_statuses = {WarStatus.finished, WarStatus.declined, WarStatus.canceled, WarStatus.expired}

    offset = (params.page - 1) * params.page_size

    # ---- ACTIVE + PENDING ----
    if params.status is None or params.status in current_statuses:
        status_filter = current_statuses if params.status is None else [params.status]

        query = select(GuildWarRequest).where(
            field_request == params.guild_id,
            GuildWarRequest.status.in_(status_filter)
        )
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        result = await session.execute(
            query.order_by(GuildWarRequest.created_at.desc()).offset(offset).limit(params.page_size)
        )
        items = result.scalars().all()

        return GuildWarListResponse(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=(total + params.page_size - 1) // params.page_size,
            results=[
                GuildWarItem(
                    id=item.id,
                    initiator_guild_id=item.initiator_guild_id,
                    target_guild_id=item.target_guild_id,
                    status=item.status,
                    created_at=item.created_at
                ) for item in items
            ]
        )

    # ---- HISTORY ----
    elif params.status in history_statuses:
        query = select(GuildWarRequestHistory).where(
            field_history == params.guild_id,
            GuildWarRequestHistory.status == params.status
        )
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        result = await session.execute(
            query.order_by(GuildWarRequestHistory.finished_at.desc()).offset(offset).limit(params.page_size)
        )
        items = result.scalars().all()

        return GuildWarHistoryListResponse(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=(total + params.page_size - 1) // params.page_size,
            results=[
                GuildWarHistoryItem(
                    id=item.id,
                    war_id=item.war_id,
                    initiator_guild_id=item.initiator_guild_id,
                    target_guild_id=item.target_guild_id,
                    status=item.status,
                    created_at=item.created_at,
                    finished_at=item.finished_at
                ) for item in items
            ]
        )

    else:
        raise HTTPException(400, detail="Invalid status filter")
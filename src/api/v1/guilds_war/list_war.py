from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from db.database import get_db
from db.models.guild_war import GuildWarRequest, GuildWarRequestHistory, WarStatus
from db.models.guild import Guild

from .schemas import GuildWarListResponse, GuildWarListParams, GuildWarHistoryListResponse, GuildWarItem, GuildWarHistoryItem

router = APIRouter()

@router.get("/list")
async def list_guild_war_requests(
    params: GuildWarListParams = Depends(GuildWarListParams.as_query_params),
    session: AsyncSession = Depends(get_db),
):
    if params.is_initiator == params.is_target:
        raise HTTPException(400, detail="Укажите ровно один из параметров: is_initiator или is_target")

    result = await session.execute(
        select(Guild.id).where(Guild.owner_id == params.owner_id)
    )
    guild_ids = [row[0] for row in result.all()]
    if not guild_ids:
        raise HTTPException(404, detail="User does not own any guilds")

    if params.is_initiator:
        guild_field_request = GuildWarRequest.initiator_guild_id
        guild_field_history = GuildWarRequestHistory.initiator_guild_id
    else:
        guild_field_request = GuildWarRequest.target_guild_id
        guild_field_history = GuildWarRequestHistory.target_guild_id

    current_statuses = {WarStatus.pending, WarStatus.active}
    history_statuses = {WarStatus.finished, WarStatus.declined, WarStatus.canceled, WarStatus.expired}

    if params.status is None:
        # По умолчанию возвращаем только текущие pending и active
        query = select(GuildWarRequest).where(
            guild_field_request.in_(guild_ids),
            GuildWarRequest.status.in_(current_statuses)
        )
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        offset = (params.page - 1) * params.page_size

        result = await session.execute(
            query.order_by(GuildWarRequest.created_at.desc()).offset(offset).limit(params.page_size)
        )
        items = result.scalars().all()

        # Преобразуем объекты SQLAlchemy в Pydantic-модели
        items_response = [GuildWarItem(
            id=item.id,
            initiator_guild_id=item.initiator_guild_id,
            target_guild_id=item.target_guild_id,
            status=item.status,
            created_at=item.created_at
        ) for item in items]

        return GuildWarListResponse(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=(total + params.page_size - 1) // params.page_size,
            results=items_response,
        )

    elif params.status in current_statuses:
        query = select(GuildWarRequest).where(
            guild_field_request.in_(guild_ids),
            GuildWarRequest.status == params.status
        )
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        offset = (params.page - 1) * params.page_size

        result = await session.execute(
            query.order_by(GuildWarRequest.created_at.desc()).offset(offset).limit(params.page_size)
        )
        items = result.scalars().all()

        
        # Преобразуем объекты SQLAlchemy в Pydantic-модели
        items_response = [GuildWarItem(
            id=item.id,
            initiator_guild_id=item.initiator_guild_id,
            target_guild_id=item.target_guild_id,
            status=item.status,
            created_at=item.created_at
        ) for item in items]

        return GuildWarListResponse(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=(total + params.page_size - 1) // params.page_size,
            results=items_response,
        )

    elif params.status in history_statuses:
        query = select(GuildWarRequestHistory).where(
            guild_field_history.in_(guild_ids),
            GuildWarRequestHistory.status == params.status
        )
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        offset = (params.page - 1) * params.page_size

        result = await session.execute(
            query.order_by(GuildWarRequestHistory.finished_at.desc()).offset(offset).limit(params.page_size)
        )
        items = result.scalars().all()

        items_response = [GuildWarHistoryItem(
            id=item.id,
            war_id=item.war_id,
            initiator_guild_id=item.initiator_guild_id,
            target_guild_id=item.target_guild_id,
            status=item.status,
            created_at=item.created_at,
            finished_at=item.finished_at,
        ) for item in items]

        return GuildWarHistoryListResponse(
            page=params.page,
            page_size=params.page_size,
            total=total,
            total_pages=(total + params.page_size - 1) // params.page_size,
            results=items_response,
        )

    else:
        raise HTTPException(400, detail="Invalid status filter")
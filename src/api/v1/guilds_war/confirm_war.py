from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select, func
from datetime import datetime, timezone
from sqlalchemy.exc import DBAPIError
from asyncpg.exceptions import DeadlockDetectedError
from aiokafka import AIOKafkaProducer
import asyncio

from settings import KafkaTopics
from db.models.guild_war import GuildWarRequest, WarStatus, GuildWarRequestHistory
from db.database import get_db

from .schemas import ConfirmWarRequest, ConfirmWarResponse
from .utils import check_guild_owner, advisory_lock_key


router = APIRouter()


@router.post("/confirm/{request_id}", response_model=ConfirmWarResponse)
async def confirm_war(
    data: ConfirmWarRequest,
    request: Request,
    request_id: int = Path(..., description="ID заявки на войну"),
    session: AsyncSession = Depends(get_db),
):
    try:
        async with session.begin():  # Обеспечивает транзакционность
            # 1. Найти заявку
            result = await session.execute(
                select(GuildWarRequest).where(GuildWarRequest.id == request_id).with_for_update()
            )
            war_request = result.scalar_one_or_none()
            if not war_request:
                raise HTTPException(404, detail="Request not found")

            if war_request.status != WarStatus.pending:
                raise HTTPException(400, detail="Request is not pending")

            # 🔐 Advisory lock через SQLAlchemy func
            guild_ids = sorted([war_request.initiator_guild_id, war_request.target_guild_id])
            lock_key = advisory_lock_key(guild_ids[0], guild_ids[1])
            await session.execute(select(func.pg_advisory_xact_lock(lock_key)))

            # 2. Проверка: владелец целевой гильдии
            await check_guild_owner(
                session=session,
                user_id=data.user_id,
                guild_id=war_request.target_guild_id
            )

            # 3. Проверка: гильдии не участвуют уже в active войне
            result = await session.execute(
                select(GuildWarRequest).where(
                    GuildWarRequest.status == WarStatus.active,
                    GuildWarRequest.id != war_request.id,
                    or_(
                        GuildWarRequest.initiator_guild_id.in_([
                            war_request.initiator_guild_id, war_request.target_guild_id
                        ]),
                        GuildWarRequest.target_guild_id.in_([
                            war_request.initiator_guild_id, war_request.target_guild_id
                        ])
                    )
                )
            )
            if result.scalar_one_or_none():
                raise HTTPException(400, detail="One of the guilds is already in an active war")

            # 4. Обновить статус
            war_request.status = WarStatus.active
            updated_at = datetime.now(timezone.utc)

            # 5. Найти и удалить конфликтующие pending-заявки
            result = await session.execute(
                select(GuildWarRequest).where(
                    GuildWarRequest.status == WarStatus.pending,
                    GuildWarRequest.id != request_id,
                    or_(
                        GuildWarRequest.initiator_guild_id.in_([
                            war_request.initiator_guild_id, war_request.target_guild_id
                        ]),
                        GuildWarRequest.target_guild_id.in_([
                            war_request.initiator_guild_id, war_request.target_guild_id
                        ])
                    )
                )
            )
            conflicting_requests = result.scalars().all()

            for req in conflicting_requests:
                session.add(GuildWarRequestHistory(
                    request_id=req.id,
                    initiator_guild_id=req.initiator_guild_id,
                    target_guild_id=req.target_guild_id,
                    status=WarStatus.declined,
                    created_at=req.created_at,
                    finished_at=updated_at
                ))
                await session.delete(req)



        response = ConfirmWarResponse(
            request_id=war_request.id,
            initiator_guild_id=war_request.initiator_guild_id,
            target_guild_id=war_request.target_guild_id,
            status=war_request.status,
            updated_at=updated_at
        )

        # Отправка в Kafka
        message = response.model_dump_json().encode("utf-8")
        producer: AIOKafkaProducer = request.app.state.producer
        try:
            await asyncio.wait_for(
            producer.send_and_wait(KafkaTopics.guild_war_confirm, message),
            timeout=3
            )
        except Exception as e:
            print(f"[Kafka ERROR] {type(e).__name__}: {e}")


        return response
    
    except DBAPIError as e:
        if isinstance(e.__cause__, DeadlockDetectedError):
            raise HTTPException(409, detail="Conflict due to concurrent request (deadlock)")
        raise


from fastapi import APIRouter, Depends, HTTPException, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from sqlalchemy.exc import DBAPIError
from asyncpg.exceptions import DeadlockDetectedError

from fastapi.security import HTTPAuthorizationCredentials
from infra.cache.redis_instance import redis

from utils.validate_token import validate_token, http_bearer
from settings import KafkaTopics
from infra.db.models.guild_war import WarStatus
from infra.db.database import get_db

from .schemas import ConfirmWarRequest, ConfirmWarResponse, ConfirmWarMessage
from .utils import get_guild_owner, send_kafka_message
from .validators.confirm_war_validation import confirm_war_validation
from .validators.delete_conflict_request import delete_conflict_request

router = APIRouter()

@router.post("/confirm/{war_id}", response_model=ConfirmWarResponse)
async def confirm_war(
    data: ConfirmWarRequest,
    request: Request,
    war_id: int = Path(..., description="ID заявки на войну"),
    session: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    try:
        payload = await validate_token(token)
        user_id = int(payload["sub"])
        if user_id != data.target_owner_id:
            raise HTTPException(status_code=403, detail="You are not the owner of this guild")

        async with session.begin():  # Обеспечивает транзакционность
            
            war_request = await confirm_war_validation(
                data=data,
                war_id=war_id,
                session=session,
            )

            initiator_owner_id = await get_guild_owner(session, war_request.initiator_guild_id)

            # Обновить статус
            war_request.status = WarStatus.active
            updated_at = datetime.now(timezone.utc)
            
            #удаляем атоматически остальные не принятые заявки
            await delete_conflict_request( 
                 data=data,
                 war_request=war_request,
                 war_id=war_id,
                 updated_at=updated_at,
                 session=session,
                 request=request
            )

            # Отправка в Kafka
            correlation_id = await redis.redis.get(f"war-correlation:{war_request.id}")

            message = ConfirmWarMessage(
                war_id=war_request.id,
                initiator_guild_id=war_request.initiator_guild_id,
                target_guild_id=war_request.target_guild_id,
                status=war_request.status,
                updated_at=updated_at,
                initiator_owner_id=initiator_owner_id,
                target_owner_id=data.target_owner_id,
                correlation_id=correlation_id
            )

            await send_kafka_message(
                request=request,
                topic=KafkaTopics.guild_war_confirm,
                message=message,
            )

        return ConfirmWarResponse(
                war_id=war_request.id,
                initiator_guild_id=war_request.initiator_guild_id,
                target_guild_id=war_request.target_guild_id,
                status=war_request.status,
                updated_at=updated_at,
                initiator_owner_id=initiator_owner_id,
                target_owner_id=data.target_owner_id,
            )
    
    except DBAPIError as e:
        if isinstance(e.__cause__, DeadlockDetectedError):
            raise HTTPException(409, detail="Conflict due to concurrent request (deadlock)")
        raise
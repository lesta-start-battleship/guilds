from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from sqlalchemy.exc import DBAPIError
from asyncpg.exceptions import DeadlockDetectedError
from fastapi.security import  HTTPAuthorizationCredentials

from utils.validate_token import validate_token, http_bearer
from settings import KafkaTopics
from cache.redis_instance import redis
from db.models.guild_war import GuildWarRequest, WarStatus
from db.database import get_db

from .schemas import DeclareWarRequest, DeclareWarResponse, DeclareWarMessage
from .utils import send_kafka_message
from .validators.declare_war_validation import declare_war_validation


router = APIRouter()

@router.post("/declare", response_model=DeclareWarResponse)
async def declare_war(
    data: DeclareWarRequest,
    request: Request, 
    session: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    try:
        await validate_token(token)

        async with session.begin():

            correlation_id = await declare_war_validation(
                data=data,
                session=session,
                request=request
            )
            
            #Создаём заявку
            new_request = GuildWarRequest(
                initiator_guild_id=data.initiator_guild_id,
                target_guild_id=data.target_guild_id,
                status=WarStatus.pending,
                created_at=datetime.now(timezone.utc)
            )
            session.add(new_request)
            await session.flush()


            #привязываем correlation_id сессии кафки к конертной войне
            war_id = new_request.id
            await redis.redis.set(f"war-correlation:{war_id}", correlation_id)


            # Отправка в Kafka
            message = DeclareWarMessage(
                war_id=new_request.id,
                initiator_guild_id=new_request.initiator_guild_id,
                target_guild_id=new_request.target_guild_id,
                status=new_request.status,
                created_at=new_request.created_at,
                correlation_id=correlation_id
            )
            await send_kafka_message(
                request=request,
                topic=KafkaTopics.guild_war_declare,
                message=message,
            )


        return DeclareWarResponse(
                war_id=new_request.id,
                initiator_guild_id=new_request.initiator_guild_id,
                target_guild_id=new_request.target_guild_id,
                status=new_request.status,
                created_at=new_request.created_at,
        )
    
    except DBAPIError as e:
        if isinstance(e.__cause__, DeadlockDetectedError):
            raise HTTPException(409, detail="Conflict due to concurrent request (deadlock)")
        raise
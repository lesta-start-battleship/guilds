from sqlalchemy import select
from sqlalchemy.orm import selectinload

from db.models.guild import Member

from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from utils.chat_util import manager, enrich_messages_with_usernames, get_username_by_id
from dependencies.chat import mongo_repo
from fastapi.encoders import jsonable_encoder
from utils.logging_config import logger


async def get_member(session: AsyncSession, user_id: int, guild_id: int) -> Member | None:
    result = await session.execute(
        select(Member)
        .where(Member.user_id == user_id, Member.guild_id == guild_id)
        .options(selectinload(Member.role))
    )
    return result.scalar_one_or_none()


async def handle_websocket(guild_id: int, user_id: int, websocket: WebSocket, db: AsyncSession):
    logger.info(f"Подключение: guild_id={guild_id}, user_id={user_id}")

    member = await get_member(db, user_id, guild_id)
    if not member:
        await handle_unauthorized_user(websocket)
        return

    await manager.connect(guild_id, websocket)

    try:
        await send_initial_history(websocket, db, guild_id)
        await listen_for_messages(websocket, db, guild_id, member)
    except WebSocketDisconnect:
        logger.warning("Клиент отключился")
    except Exception as e:
        logger.warning("Общая ошибка в WebSocket:", e)
    finally:
        manager.disconnect(guild_id, websocket)
        logger.warning("Соединение удалено из менеджера")



async def handle_unauthorized_user(websocket: WebSocket):
    logger.warning("Пользователь не найден в гильдии или не имеет доступа")
    await manager.connect_user_only(
        websocket,
        {"type": "error", "data": ["Доступ отказан: вы не являетесь членом этой гильдии."]},
        close_code=1008
    )


async def send_initial_history(websocket: WebSocket, db: AsyncSession, guild_id: int):
    try:
        history = await mongo_repo.get_messages_by_guild(guild_id, skip=0, limit=2)
        enriched = await enrich_messages_with_usernames(db, history)
        await websocket.send_json({
            "type": "history",
            "data": enriched,
            "meta": {"skip": 0, "limit": 10, "count": len(enriched)}
        })
        logger.info(f"История сообщений отправлена (кол-во: {len(enriched)})")
    except Exception as e:
        logger.warning("Ошибка при загрузке истории сообщений:", e)


async def listen_for_messages(websocket: WebSocket, db: AsyncSession, guild_id: int, member):
    while True:
        data = await websocket.receive_json()
        logger.info(f"Получено сообщение от {member.user_id}: {data}")

        msg_type = data.get("type")
        payload = data.get("payload", {})

        if msg_type == "history":
            await handle_history_request(websocket, db, guild_id, payload)
        else:
            await handle_new_message(db, guild_id, member, data)


async def handle_history_request(websocket: WebSocket, db: AsyncSession, guild_id: int, payload: dict):
    skip = int(payload.get("skip", 0))
    limit = int(payload.get("limit", 10))
    try:
        history = await mongo_repo.get_messages_by_guild(guild_id, skip=skip, limit=limit)
        enriched = await enrich_messages_with_usernames(db, history)
        await websocket.send_json({
            "type": "history",
            "data": enriched,
            "meta": {"skip": skip, "limit": limit, "count": len(enriched)}
        })
        logger.info(f"История (skip={skip}, limit={limit}) отправлена")
    except Exception as e:
        logger.warning("Ошибка при загрузке истории:", e)


async def handle_new_message(db: AsyncSession, guild_id: int, member, data: dict):
    message = {
        "user_id": member.user_id,
        "guild_id": member.guild_id,
        "content": data.get("content", "")
    }

    try:
        saved = await mongo_repo.save_message(message)
        username = await get_username_by_id(db, saved.user_id)
        outgoing = jsonable_encoder(saved)
        outgoing["username"] = username
        await manager.broadcast(guild_id, outgoing)
        logger.info("Сообщение разослано всем подключённым клиентам")
    except Exception as e:
        logger.warning("Ошибка при сохранении/рассылке сообщения:", e)

import asyncio
from typing import Any

from fastapi import WebSocketDisconnect, Depends, APIRouter, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.database import get_db
from dependencies.chat import mongo_repo
from services.chat_service import get_member
from utils.chat_util import manager, enrich_messages_with_usernames, get_username_by_id
from utils.logging_config import logger

router = APIRouter()

active_connections = {}


@router.websocket("/ws/guild/{guild_id}/{user_id}")
async def guild_websocket(
        guild_id: int,
        user_id: int,
        websocket: WebSocket,
        db: AsyncSession = Depends(get_db)
):
    logger.info(f"📡 Подключение: guild_id={guild_id}, user_id={user_id}")

    member = await get_member(db, user_id, guild_id)
    if not member:
        logger.warning("❌ Пользователь не найден в гильдии или не имеет доступа")
        await manager.connect_user_only(
            websocket,
            {"type": "error",
             "data": ["Доступ отказан: вы не являетесь членом этой гильдии."]},
            close_code=1008
        )
        return
    logger.info("✅ Пользователь подтверждён как участник гильдии")

    await manager.connect(guild_id, websocket)

    try:
        history = await mongo_repo.get_messages_by_guild(guild_id, skip=0, limit=2)
        enriched = await enrich_messages_with_usernames(db, history)
        await websocket.send_json({
            "type": "history",
            "data": enriched,
            "meta": {"skip": 0, "limit": 10, "count": len(enriched)}
        })
        logger.info(f"📜 История сообщений отправлена (кол-во: {len(enriched)})")
    except Exception as e:
        logger.warning("❌ Ошибка при загрузке истории сообщений:", e)

    try:
        while True:
            data: Any = await websocket.receive_json()
            logger.info(f"📨 Получено сообщение от {user_id}: {data}")

            msg_type = data.get("type")
            payload = data.get("payload", {})

            if msg_type == "history":
                skip = int(payload.get("skip", 0))
                limit = int(payload.get("limit", 10))
                try:
                    history = await mongo_repo.get_messages_by_guild(guild_id, skip=skip, limit=limit)
                    enriched = await enrich_messages_with_usernames(db, history)
                    await websocket.send_json({
                        "type": "history",
                        "data": enriched,
                        "meta": {
                            "skip": skip,
                            "limit": limit,
                            "count": len(enriched)
                        }
                    })
                    logger.info(f"📜 История (skip={skip}, limit={limit}) отправлена")
                except Exception as e:
                    logger.warning("❌ Ошибка при загрузке истории:", e)
                continue

            message = {
                "user_id": member.user_id,
                "guild_id": member.guild_id,
                "content": payload.get("content", "")
            }

            try:
                saved = await mongo_repo.save_message(message)
                username = await get_username_by_id(db, saved.user_id)
                outgoing = jsonable_encoder(saved)
                outgoing["username"] = username
                await manager.broadcast(guild_id, outgoing)
                logger.info("📢 Сообщение разослано всем подключённым клиентам")
            except Exception as e:
                logger.warning("❌ Ошибка при сохранении/рассылке сообщения:", e)

    except WebSocketDisconnect:
        logger.warning("🔌 Клиент отключился")
    except Exception as e:
        logger.warning("❌ Общая ошибка в WebSocket:", e)
    finally:
        manager.disconnect(guild_id, websocket)
        logger.warning("🧹 Соединение удалено из менеджера")



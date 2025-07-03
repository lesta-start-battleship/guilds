import asyncio

from fastapi import WebSocketDisconnect, Depends
from fastapi import APIRouter, WebSocket
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from dependencies.chat import mongo_repo
from services.chat_service import get_member
from utils.chat_util import manager

router = APIRouter()

active_connections = {}


@router.websocket("/ws/guild/{guild_id}/{user_id}")
async def guild_chat_ws(
    guild_id: int,
    user_id: int,
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    member = await get_member(db, user_id, guild_id)
    mongo = mongo_repo
    if not member:
        await websocket.accept()
        await websocket.send_json({"error": "Access denied: you are not a member of this guild."})
        await websocket.close()
        return

    await manager.connect(guild_id, websocket)

    try:
        history = await mongo.get_messages_by_guild(guild_id)
        await asyncio.sleep(0.1)
        await websocket.send_json({
            "type": "history",
            "data": jsonable_encoder(history)
        })
    except Exception as e:
        print("❌ Ошибка при загрузке истории:", e)

    try:
        while True:
            data = await websocket.receive_json()
            print("📩 Получено сообщение от клиента:", data)

            message_data = {
                "guild_id": guild_id,
                "user_id": data["user_id"],
                "user_name": data["user_name"],
                "content": data["content"],
            }

            try:
                saved = await mongo.save_message(message_data)
                print("✅ Сохранено сообщение:", saved)
                await manager.broadcast(guild_id, jsonable_encoder(saved))
            except Exception as e:
                print("❌ Ошибка при сохранении в Mongo:", e)

    except WebSocketDisconnect:
        print("🔌 Клиент отключился")
    except Exception as e:
        print("❌ Общая ошибка:", e)
    finally:
        manager.disconnect(guild_id, websocket)
        print("🧹 Соединение удалено")



import asyncio
from fastapi import WebSocketDisconnect, Depends, APIRouter, WebSocket
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
    print(f"📡 [CONNECT] Попытка подключения: guild_id={guild_id}, user_id={user_id}")

    try:
        await websocket.accept()
        print("✅ WebSocket соединение принято")
    except Exception as e:
        print(f"❌ Ошибка при попытке принять WebSocket соединение: {e}")
        return

    try:
        member = await get_member(db, user_id, guild_id)
        if not member:
            print("❌ Пользователь не найден в гильдии или не имеет доступа")
            await websocket.send_json({"error": "Access denied: you are not a member of this guild."})
            await websocket.close()
            return
        print("✅ Пользователь подтверждён как участник гильдии")

        await manager.connect(guild_id, websocket)
        print("✅ Соединение добавлено в менеджер подключений")

        # Отправляем историю сообщений
        try:
            history = await mongo_repo.get_messages_by_guild(guild_id)
            await asyncio.sleep(0.1)
            await websocket.send_json({
                "type": "history",
                "data": jsonable_encoder(history)
            })
            print(f"📜 История сообщений отправлена (кол-во: {len(history)})")
        except Exception as e:
            print("❌ Ошибка при загрузке истории сообщений:", e)

        # Получение и отправка новых сообщений
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
                saved = await mongo_repo.save_message(message_data)
                print("✅ Сохранено сообщение:", saved)
                await manager.broadcast(guild_id, jsonable_encoder(saved))
                print("📢 Сообщение разослано всем подключённым клиентам")
            except Exception as e:
                print("❌ Ошибка при сохранении/рассылке сообщения:", e)

    except WebSocketDisconnect:
        print("🔌 Клиент отключился")
    except Exception as e:
        print("❌ Общая ошибка в обработчике WebSocket:", e)
    finally:
        manager.disconnect(guild_id, websocket)
        print("🧹 Соединение удалено из менеджера")

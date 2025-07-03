import asyncio

from fastapi import WebSocketDisconnect
from fastapi import APIRouter, WebSocket
from services.mongo_instance import mongo_repo
from fastapi.encoders import jsonable_encoder

router = APIRouter()

active_connections = {}


@router.websocket("/ws/guild/{guild_id}/{user_id}")
async def guild_chat_ws(guild_id: int, user_id: int, websocket: WebSocket):
    await websocket.accept()
    repo = mongo_repo

    # Инициализируем список подключений для гильдии
    if guild_id not in active_connections:
        active_connections[guild_id] = []
    active_connections[guild_id].append(websocket)

    try:
        history = await repo.get_messages_by_guild(guild_id)
        print("📜 История сообщений:", history)  # Логируем историю сообщений
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
            print("Получено сообщение от клиента:", data)

            message_data = {
                "guild_id": guild_id,
                "user_id": data["user_id"],
                "user_name": data["user_name"],
                "content": data["content"],
            }

            try:
                saved = await repo.save_message(message_data)
                print("Сохранено сообщение:", saved)
            except Exception as e:
                print("Ошибка при сохранении в Mongo:", e)
                continue

            for conn in active_connections.get(guild_id, []):
                try:
                    await conn.send_json(jsonable_encoder(saved))
                except Exception as e:
                    print("❌ Ошибка при отправке клиенту:", e)

    except WebSocketDisconnect:
        print("🔌 Клиент отключился")
    except Exception as e:
        print("❌ Общая ошибка:", e)
    finally:
        try:
            active_connections[guild_id].remove(websocket)
            print("🧹 Соединение удалено из списка active_connections")
        except (KeyError, ValueError):
            pass


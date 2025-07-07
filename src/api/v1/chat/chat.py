import asyncio
from typing import Any

from fastapi import WebSocketDisconnect, Depends, APIRouter, WebSocket
from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_db
from dependencies.chat import mongo_repo
from services.chat_service import get_member
from utils.chat_util import manager

router = APIRouter()

active_connections = {}


@router.websocket("/ws/guild/{guild_id}/{user_id}")
async def guild_websocket(
        guild_id: int,
        user_id: int,
        websocket: WebSocket,
        db: AsyncSession = Depends(get_db)
):
    print(f"📡 Подключение: guild_id={guild_id}, user_id={user_id}")

    member = await get_member(db, user_id, guild_id)
    if not member:
        print("❌ Пользователь не найден в гильдии или не имеет доступа")
        await manager.connect_user_only(
            websocket,
            {"type": "error",
            "data": ["Доступ отказан: вы не являетесь членом этой гильдии."]},
            close_code=1008
        )
        return
    print("✅ Пользователь подтверждён как участник гильдии")

    await manager.connect(guild_id, websocket)

    try:
        history = await mongo_repo.get_messages_by_guild(guild_id)
        # todo добавить пагинацию и написать функуию которая будет добавлять username в каждое сообщение
        await asyncio.sleep(0.1)
        await websocket.send_json({
            "type": "history",
            "data": jsonable_encoder(history)
        })
        print(f"📜 История сообщений отправлена (кол-во: {len(history)})")
    except Exception as e:
        print("❌ Ошибка при загрузке истории сообщений:", e)

    try:
        while True:
            data: Any = await websocket.receive_json()
            print(f"📨 Получено сообщение от {user_id}: {data}")

            # Пример обогащения сообщения
            message = {
                "user_id": member.user_id,
                "guild_id": member.guild_id,
                # "user_name": data["user_name"],
                "content": data.get("content", ""),
            }

            try:
                saved = await mongo_repo.save_message(message)
                print("✅ Сохранено сообщение:", saved)
                # todo здесь так же нужно будет использовать функцию которая подменяет имя пользователя в ззависимости от ID
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


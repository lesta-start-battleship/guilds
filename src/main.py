import asyncio
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager

from fastapi.encoders import jsonable_encoder
from fastapi.openapi.utils import get_openapi
from aiokafka import AIOKafkaProducer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.v1 import router as v1
from db.database import get_db
from dependencies.chat import mongo_repo
from services.chat_service import get_member
from settings import settings, KAFKA_BOOTSTRAP_SERVERS
from db.database import get_db
from utils.chat_util import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создание Kafka producer и сохранение в app.state
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    await producer.start()
    print("Kafka producer started")
    app.state.producer = producer

    # Запуск приложения
    yield

    # Завершение работы продюсера
    await app.state.producer.stop()
    print("Kafka producer stopped")

app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug,
    lifespan=lifespan
)

app.include_router(v1)


@app.websocket("/ws/guild/{guild_id}/{user_id}")
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


# не много кастомизируем наш Swagger для документирования ws эндпоинта
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["paths"]["/api/v1/ws/guild/{guild_id}/{user_id}"] = {
        "get": {
            "summary": "Подключение к WebSocket для гильдии и пользователя",
            "description": "Для подключения к серверу WebSocket нужно:"
                           "указать ID конкретной гильдии и пользователя. Отправьте сообщение и "
                           "получите ответ."
                           "Пример подключения: ws://host:port/api/v1/ws/guild/1/1",
            "tags": ["Chat"],
            "parameters": [
                {
                    "name": "guild_id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "integer",
                    }
                },
                {
                    "name": "user_id",
                    "in": "path",
                    "required": True,
                    "schema": {
                        "type": "integer",
                    }
                }
            ],
            "responses": {
                "101": {
                    "description": "Протоколы переключения - Клиент переключает протоколы, запрашиваемые сервером.",
                }
            }
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

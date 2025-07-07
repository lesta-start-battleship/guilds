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

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    openapi_schema["paths"]["/api/v1/chat/ws/guild/{guild_id}/{user_id}"] = {
        "get": {
            "summary": "Подключение к WebSocket для гильдии и пользователя",
            "description": "Для подключения к серверу WebSocket нужно:"
                           "указать ID конкретной гильдии и пользователя. Отправьте сообщение и "
                           "получите ответ."
                           "Пример подключения: ws://host:port/api/v1/chat/ws/guild/guild_id/user_id",
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

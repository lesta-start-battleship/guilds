from fastapi import FastAPI
from contextlib import asynccontextmanager

from fastapi.openapi.utils import get_openapi
from aiokafka import AIOKafkaProducer
import asyncio

from api.v1 import router as v1
from api.v1.guilds_war.consumers.consume_guild_declare_responses import consume_guild_declare_responses
from settings import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск Kafka Producer
    producer = AIOKafkaProducer(bootstrap_servers=settings.kafka_service)
    await producer.start()
    print("Kafka producer started")
    app.state.producer = producer

    # Запуск Kafka Consumer в фоне
    consumer_task = asyncio.create_task(consume_guild_declare_responses(app))

    yield

    # Завершение
    await producer.stop()
    print("Kafka producer stopped")

    consumer_task.cancel()
    try:
        await consumer_task
    except asyncio.CancelledError:
        print("Kafka consumer task cancelled")

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

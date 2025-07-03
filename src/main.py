from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from api.v1.start_endpoints import router as start
from api.v1.guild import router as guild
from api.v1.member import router as member
from api.v1.chat import router as chat
from api.v1.guilds_war.routers import router as guild_war_router

from settings import settings


app = FastAPI(
    title=settings.project.title,
    description=settings.project.description,
    version=settings.project.release_version,
    debug=settings.debug
)

app.include_router(start, prefix="/api/v1", tags=["old"])
app.include_router(guild, prefix='/api/v1/guild', tags=['guild'])
app.include_router(member, prefix='/api/v1/member', tags=['member'])
app.include_router(chat, prefix="/api/v1", tags=["chat"])
app.include_router(guild_war_router, prefix="/api/v1", tags=["Guilds War"])

app.include_router(guild_war_router, prefix="/api/v1", tags=["Guilds War"])


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

import asyncio

from fastapi import status, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

from schemas.chat import CreateChatResponseSchema, CreateChatRequestSchema, ErrorSchema
from services.chat_service import MongoChatRepository
# from services.chat_service import ChatService
from utils.chat_util import manager
from fastapi import APIRouter, WebSocket
from uuid import uuid4
from services.mongo_instance import mongo_repo
from fastapi.encoders import jsonable_encoder

router = APIRouter()
# chat_service = ChatService(get_chat_repository())


@router.post(
    '/',
    # response_model=CreateChatResponseSchema,
    status_code=status.HTTP_201_CREATED,
    description='Эндпоинт создаёт новый чат, если чат с таким названием существует, то возвращается 400 ошибка',
    responses={
        status.HTTP_201_CREATED: {'model': CreateChatResponseSchema},
        status.HTTP_400_BAD_REQUEST: {'model': ErrorSchema},
    },
)
async def create_chat_handler(schema: CreateChatRequestSchema):
    ''' Создать новый чат. '''
    # добавить проверку пользователя
    # добавить d jndtn uid чата
    return {"status_code": status.HTTP_201_CREATED, "schema": schema}



active_connections = {}

@router.websocket("/ws/guild/{guild_id}")
async def guild_chat_ws(guild_id: int, websocket: WebSocket):
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
        # 🔄 Получение и отправка сообщений
        while True:
            data = await websocket.receive_json()
            print("📥 Получено сообщение от клиента:", data)

            message_data = {
                "guild_id": guild_id,
                "user_id": data["user_id"],
                "user_name": data["user_name"],
                "content": data["content"],
            }

            try:
                saved = await repo.save_message(message_data)
                print("💾 Сохранено сообщение:", saved)
            except Exception as e:
                print("❌ Ошибка при сохранении в Mongo:", e)
                continue

            # 📤 Рассылаем сообщение всем участникам гильдии
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
        # 🧹 Удаляем соединение при отключении
        try:
            active_connections[guild_id].remove(websocket)
            print("🧹 Соединение удалено из списка active_connections")
        except (KeyError, ValueError):
            pass


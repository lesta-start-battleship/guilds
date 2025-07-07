from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from utils.logging_config import logger
from utils.chat_util import manager


async def handle_disconnect(guild_id: int, websocket: WebSocket):
    logger.warning("🔌 Клиент отключился")
    manager.disconnect(guild_id, websocket)
    logger.warning("🧹 Соединение удалено из менеджера")


async def handle_general_exception(guild_id: int, websocket: WebSocket, e: Exception):
    logger.warning("❌ Общая ошибка в WebSocket:", exc_info=e)
    manager.disconnect(guild_id, websocket)
    logger.warning("🧹 Соединение удалено из менеджера")
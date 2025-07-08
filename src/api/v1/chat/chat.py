from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infra.db.database import get_db
from dependencies.chat import mongo_repo
from services.chat_service import get_member
from utils.chat_util import manager, enrich_messages_with_usernames, get_username_by_id
from utils.logging_config import logger
from services.chat_service import handle_websocket

router = APIRouter()

@router.websocket("/ws/guild/{guild_id}/{user_id}")
async def guild_websocket(
    guild_id: int,
    user_id: int,
    websocket: WebSocket,
    db: AsyncSession = Depends(get_db)
):
    await handle_websocket(guild_id, user_id, websocket, db)

# {
#   "type": "history", "error",
#   "payload": {
#     "skip": 0,
#     "limit": 10
#   }
# }
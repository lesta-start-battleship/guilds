from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from infra.db.database import get_db
from monitoring.metrics import metrics
from services.chat_service import handle_websocket
from utils.validate_token import http_bearer, validate_token

router = APIRouter()


@router.websocket("/ws/guild/{guild_id}")
async def guild_websocket(
        guild_id: int,
        websocket: WebSocket,
        db: AsyncSession = Depends(get_db),
        token: HTTPAuthorizationCredentials = Depends(http_bearer),
):
    metrics.websocket_connections_total.labels(path=str(websocket.url.path)).inc()
    payload = await validate_token(token)
    user_id = int(payload["sub"])
    await handle_websocket(guild_id, user_id, websocket, db)

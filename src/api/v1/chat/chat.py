from fastapi import APIRouter, WebSocket, WebSocketException, Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from infra.db.database import get_db
from monitoring.metrics import metrics
from services.chat_service import handle_websocket
from utils.validate_token import validate_token

router = APIRouter()


async def get_token_websocket(websocket: WebSocket):
    auth_header = websocket.headers.get('Authorization')
    if not auth_header:
        raise WebSocketException(code=1008, reason="Missing Authorization header")
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != 'bearer':
            raise WebSocketException(code=1008, reason="Invalid authentication scheme")
        return HTTPAuthorizationCredentials(scheme=scheme, credentials=token)
    except ValueError:
        raise WebSocketException(code=1008, reason="Invalid Authorization header format")


@router.websocket("/ws/guild/{guild_id}")
async def guild_websocket(
        guild_id: int,
        websocket: WebSocket,
        db: AsyncSession = Depends(get_db),
        token: HTTPAuthorizationCredentials = Depends(get_token_websocket),
):
    await websocket.accept()
    metrics.websocket_connections_total.labels(path=str(websocket.url.path)).inc()
    payload = await validate_token(token.credentials)
    user_id = int(payload["sub"])
    await handle_websocket(guild_id, user_id, websocket, db)

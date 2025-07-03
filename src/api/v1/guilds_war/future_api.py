from fastapi import APIRouter, HTTPException, Path, WebSocket, WebSocketDisconnect
from pydantic import BaseModel,  conlist
from datetime import datetime
from typing import Dict, List

router = APIRouter()


# Отменить запрос на войну вручную
@router.post("/cancel")
async def cancel_war():
    return {
        "status": "cancelled",
        "message": f"Guild  cancelled the war request"
    }

# Завершение войны (заглушка)
@router.post("/finish")
async def finish_war():
    return {
        "status": "finished",
        "message": "Guild war has been finished"
    }


@router.get("/ws-doc", include_in_schema=True)
async def websocket_doc():
    return {
        "url": "/api/v1/guild/war/ws/{guild_id}",
        "method": "WebSocket",
        "note": "Подключитесь через WebSocket-клиент. Пример: ws://localhost:8000/api/v1/guild/war/ws/1"
    }


active_connections: Dict[int, List[WebSocket]] = {}  # guild_id → [WebSocket]

@router.websocket("/ws/{guild_id}")
async def guild_socket(websocket: WebSocket, guild_id: int):
    await websocket.accept()
    active_connections.setdefault(guild_id, []).append(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            # 📢 Рассылаем ВСЕМ клиентам в этой гильдии
            for conn in active_connections[guild_id]:
                if conn != websocket:
                    await conn.send_text(f"[guild {guild_id}] {message}")
    except WebSocketDisconnect:
        active_connections[guild_id].remove(websocket)
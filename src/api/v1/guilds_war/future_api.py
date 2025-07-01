from fastapi import APIRouter, HTTPException, Path, WebSocket, WebSocketDisconnect
from pydantic import BaseModel,  conlist
from datetime import datetime
from typing import Dict, List

router = APIRouter()

# 📦 Схемы запросов
class DeclareWarRequest(BaseModel):
    target_guild_id: int  # кто подтверждает войну
    initiator_guild_id: int  # кто начал войну


class ConfirmWarRequest(BaseModel):
    target_guild_id: int  # кто подтверждает войну
    initiator_guild_id: int  # кто начал войну

class DeclineWarRequest(BaseModel):
    guild_id: int  # инициатор, который отменяет войну

# 🔹 Объявить войну
@router.post("/declare")
async def declare_war(data: DeclareWarRequest):
    return {
        "status": "pending",
        "message": f"Guild {data.initiator_guild_id} declared war on Guild {data.target_guild_id}"
    }

# 🔹 Подтвердить войну
@router.post("/confirm")
async def confirm_war(data: ConfirmWarRequest):
    return {
        "status": "active",
        "message": f"Guild {data.guild_id} confirmed the war"
    }


# 🔹 Отменить запрос на войну
@router.post("/decline")
async def decline_war(data: DeclineWarRequest):
    return {
        "status": "cancelled",
        "message": f"Guild {data.guild_id} cancelled the war request"
    }


# 🔚 Завершение войны (заглушка)
@router.post("/finish")
async def finish_war():
    return {
        "status": "finished",
        "message": "Guild war has been finished"
    }



@router.get("/ws-doc", include_in_schema=True)
async def websocket_doc():
    return {
        "url": "/guild/war/ws/{guild_id}",
        "method": "WebSocket",
        "note": "Подключитесь через WebSocket-клиент. Пример: wss://example.com/guild/war/ws/1"
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
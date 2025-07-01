from fastapi import status, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from fastapi.websockets import WebSocketState
from typing import List


# Добавляем менеджер соединений WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            if connection.client_state == WebSocketState.CONNECTED:
                await connection.send_text(message)


manager = ConnectionManager()

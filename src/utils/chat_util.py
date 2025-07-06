from fastapi import status, WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter
from fastapi.websockets import WebSocketState
from typing import List


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, guild_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(guild_id, []).append(websocket)

    def disconnect(self, guild_id: int, websocket: WebSocket):
        try:
            self.active_connections[guild_id].remove(websocket)
            if not self.active_connections[guild_id]:
                del self.active_connections[guild_id]
        except (KeyError, ValueError):
            pass

    async def broadcast(self, guild_id: int, message: dict):
        connections = self.active_connections.get(guild_id, [])
        for connection in connections:
            if connection.client_state == WebSocketState.CONNECTED:
                await connection.send_json(message)

    @staticmethod
    async def connect_user_only(websocket: WebSocket, message: dict, close_code: int = 1008):
        try:
            await websocket.accept()
            await websocket.send_json(message)
        except Exception as e:
            print(f"[connect_user_only] Ошибка при отправке: {e}")
        finally:
            await websocket.close(code=close_code)



manager = ConnectionManager()

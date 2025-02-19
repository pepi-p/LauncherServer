from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from models import GameTag
import crud
import json

# WebSocketを管理するクラス
class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    # 接続を追加する
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    # 接続を削除する
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    # 送信されたデータを見る
    async def receive_texts(self):
        texts = []
        for connection in self.active_connections:
            texts.append(connection.receive_text())
        return texts

# タグ用のWebSocket
class TagWebSocketManager(WebSocketManager):
    def __init__(self):
        super().__init__()
    
    # 登録済みの接続に一括して送る
    async def broadcast(self, db_tags: list[GameTag]): # , sender: WebSocket
        data = {}
        for db_tag in db_tags:
            data[db_tag.id] = db_tag.tag
        for connection in self.active_connections:
            # if connection != sender:
            await connection.send_json(data)

# ランチャー用のWebSocket
class LauncherWebSocketManager(WebSocketManager):
    def __init__(self):
        super().__init__()
    
    # 登録済みの接続に一括して送る
    async def broadcast(self, cmd: str, id: int):
        print(f"{cmd}: {id}")
        data = {}
        data["command"] = cmd
        data["id"] = id
        for connection in self.active_connections:
            await connection.send_json(data)

# 初期化
router = APIRouter()
tag_ws_manager = TagWebSocketManager()
launcher_ws_manager = LauncherWebSocketManager()

# タグのWebSocketのエンドポイント
@router.websocket("/ws/web")
async def websocket_endpoint(websocket: WebSocket):
    await tag_ws_manager.connect(websocket)
    try:
        pass
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        tag_ws_manager.disconnect(websocket)

# ランチャーのWebSocketのエンドポイント
@router.websocket("/ws/launcher")
async def websocket_endpoint(websocket: WebSocket):
    await launcher_ws_manager.connect(websocket)
    try:
        pass
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(data)
    except WebSocketDisconnect:
        launcher_ws_manager.disconnect(websocket)
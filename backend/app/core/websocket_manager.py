from typing import Dict, List
from fastapi import WebSocket

class ConnectionManager:
    """
    Manages active WebSocket connections to broadcast step-by-step timeline updates
    for processing document IDs.
    """
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, document_id: str, websocket: WebSocket):
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
        self.active_connections[document_id].append(websocket)
        print(f"[WS] Connected client for document: {document_id}")

    def disconnect(self, document_id: str, websocket: WebSocket):
        if document_id in self.active_connections:
            self.active_connections[document_id].remove(websocket)
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]
        print(f"[WS] Disconnected client for document: {document_id}")

    async def broadcast_to_document(self, document_id: str, message: dict):
        if document_id in self.active_connections:
            for connection in self.active_connections[document_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    print(f"[WS] Error sending message: {e}")

manager = ConnectionManager()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Set, Dict, Any
import asyncio, datetime

app = FastAPI(title="HarmWatch Bridge", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class IngestItem(BaseModel):
    text: str
    source: str = "unknown"
    author: str | None = None
    timestamp: str | None = None
    platform: str | None = None
    url: str | None = None

class Manager:
    def __init__(self):
        self.clients: Set[WebSocket] = set()
        self.lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self.lock:
            self.clients.add(ws)

    async def disconnect(self, ws: WebSocket):
        async with self.lock:
            self.clients.discard(ws)

    async def broadcast(self, msg: Dict[str, Any]):
        dead = []
        async with self.lock:
            for ws in self.clients:
                try:
                    await ws.send_json(msg)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.clients.discard(ws)

manager = Manager()

@app.websocket("/stream")
async def stream(ws: WebSocket):
    await manager.connect(ws)
    try:
        while True:
            await ws.receive_text()  # keepalive
    except WebSocketDisconnect:
        await manager.disconnect(ws)

@app.post("/ingest")
async def ingest(item: IngestItem):
    payload = item.dict()
    if not payload.get("timestamp"):
        payload["timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    await manager.broadcast(payload)
    return {"ok": True}

@app.get("/health")
async def health():
    return {"status": "ok", "clients": len(manager.clients)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

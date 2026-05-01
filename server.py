"""
Minimal WebSocket server for local assistant.
"""

import asyncio
import os
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from agent import LocalAssistantAgent
from config import Settings

app = FastAPI(title="Local AI Assistant WS")
agent = LocalAssistantAgent(Settings())
BRIDGE_TOKEN = os.getenv("AI_BRIDGE_TOKEN", "").strip()


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.websocket("/ws/chat")
async def chat_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    loop = asyncio.get_running_loop()

    try:
        while True:
            payload: Dict[str, Any] = await websocket.receive_json()
            text = str(payload.get("message", "")).strip()
            web_mode = bool(payload.get("web_mode", False))
            token = str(payload.get("token", "")).strip()

            if BRIDGE_TOKEN and token != BRIDGE_TOKEN:
                await websocket.send_json(
                    {"type": "error", "message": "Yetkisiz istek: token gecersiz."}
                )
                continue

            if not text:
                await websocket.send_json(
                    {"type": "error", "message": "Bos mesaj gonderilemez."}
                )
                continue

            await websocket.send_json(
                {"type": "status", "message": "Asistan dusunuyor..."}
            )

            # Run blocking inference on thread pool to keep WS responsive.
            answer = await loop.run_in_executor(
                None, lambda: agent.handle(text, force_web=web_mode, disable_web=not web_mode)
            )

            await websocket.send_json({"type": "answer", "message": answer})
    except WebSocketDisconnect:
        return


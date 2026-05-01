"""
Minimal Ollama client helpers.
"""

import json
from typing import Dict, List
from urllib import error, request

from config import Settings


class OllamaClient:
    def __init__(self, settings: Settings):
        self.settings = settings

    def chat(self, messages: List[Dict[str, str]], stream: bool = False) -> str:
        payload = {
            "model": self.settings.model_name,
            "messages": messages,
            "stream": stream,
            "options": {
                "temperature": self.settings.temperature,
                "top_p": self.settings.top_p,
                "num_ctx": self.settings.num_ctx,
                "num_batch": self.settings.num_batch,
                "num_gpu": self.settings.num_gpu,
                "num_thread": self.settings.num_thread,
            },
            "keep_alive": self.settings.keep_alive,
        }
        req = request.Request(
            url=f"{self.settings.ollama_base_url}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=120) as response:
                raw = response.read().decode("utf-8")
                parsed = json.loads(raw)
                return parsed["message"]["content"]
        except error.URLError as exc:
            return f"Ollama baglanti hatasi: {exc}"
        except Exception as exc:  # noqa: BLE001
            return f"LLM cagrisi basarisiz: {exc}"


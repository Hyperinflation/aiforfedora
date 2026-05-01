"""
Simple JSON chat memory.
"""

import json
from pathlib import Path
from typing import Dict, List


class ChatMemory:
    def __init__(self, history_file: Path, max_messages: int = 20):
        self.history_file = history_file
        self.max_messages = max_messages
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> List[Dict[str, str]]:
        if not self.history_file.exists():
            return []
        try:
            return json.loads(self.history_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return []

    def save(self, messages: List[Dict[str, str]]) -> None:
        trimmed = messages[-self.max_messages :]
        self.history_file.write_text(
            json.dumps(trimmed, ensure_ascii=False, indent=2), encoding="utf-8"
        )


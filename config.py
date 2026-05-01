"""
Application configuration for local Qwen assistant.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class Settings:
    ollama_base_url: str = "http://localhost:11434"
    model_name: str = "qwen3:8b"
    # Keep context window modest for low VRAM.
    num_ctx: int = 2048
    # Smaller batch improves memory usage on limited GPUs.
    num_batch: int = 64
    # Use as many layers as possible on GPU (Ollama/llama.cpp style).
    num_gpu: int = 999
    # Limit CPU threads to reduce CPU heat while GPU is active.
    num_thread: int = 4
    temperature: float = 0.2
    top_p: float = 0.9
    keep_alive: str = "30m"

    history_file: Path = Path("data/chat_history.json")
    docs_path: Path = Path("data/knowledge")
    max_history_messages: int = 20
    rag_top_k: int = 3

    # Conservative whitelist for shell command names.
    allowed_commands: List[str] = field(
        default_factory=lambda: [
            "ls",
            "pwd",
            "echo",
            "cat",
            "head",
            "tail",
            "wc",
            "grep",
            "rg",
            "find",
            "python",
            "python3",
            "pip",
            "pip3",
            "git",
            "uname",
            "whoami",
            "date",
            "df",
            "du",
            "free",
            "ps",
            "top",
            "curl",
            "wget",
        ]
    )

    blocked_patterns: List[str] = field(
        default_factory=lambda: [
            "rm -rf",
            "shutdown",
            "reboot",
            "mkfs",
            "dd if=",
            ":(){:|:&};:",
            "chmod 777 /",
            "sudo ",
            "> /dev/sd",
            "kill -9 1",
        ]
    )


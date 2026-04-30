#!/usr/bin/env python3

"""
Fedora-side CLI client that forwards prompts to Windows AI host over WebSocket.
"""

import argparse
import json
import sys

from websocket import create_connection


def ask_remote(server_url: str, message: str, web_mode: bool, token: str) -> str:
    ws = create_connection(server_url, timeout=120)
    try:
        ws.send(
            json.dumps(
                {
                    "message": message,
                    "web_mode": web_mode,
                    "token": token,
                }
            )
        )
        while True:
            raw = ws.recv()
            data = json.loads(raw)
            msg_type = data.get("type")
            if msg_type == "answer":
                return str(data.get("message", ""))
            if msg_type == "error":
                return f"Hata: {data.get('message', 'Bilinmeyen hata')}"
    finally:
        ws.close()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Fedora istemcisi: soruyu Windows AI host'a iletir."
    )
    parser.add_argument(
        "--server",
        default="ws://127.0.0.1:8000/ws/chat",
        help="Windows makinedeki WS endpoint",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Web modu acik: guncel bilgi icin internet aracini zorlar",
    )
    parser.add_argument(
        "--token",
        default="",
        help="Sunucu token (AI_BRIDGE_TOKEN ile ayni olmali)",
    )
    parser.add_argument("prompt", nargs="+", help="Sorulacak metin")
    args = parser.parse_args()

    text = " ".join(args.prompt).strip()
    if not text:
        print("Bos prompt gonderilemez.")
        return 1

    answer = ask_remote(args.server, text, args.web, args.token)
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


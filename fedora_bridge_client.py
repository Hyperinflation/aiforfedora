#!/usr/bin/env python3

"""
Fedora-side CLI client that forwards prompts to Windows AI host over WebSocket.
"""

import argparse
import json
import os
import shutil
import subprocess
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


def run_interactive_chat(server_url: str, web_mode: bool, token: str) -> int:
    print("Local AI Bridge chat basladi. Cikmak icin /quit yaz.")
    while True:
        try:
            text = input("Sen> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCikis yapildi.")
            return 0

        if not text:
            continue
        if text.lower() in {"/quit", "/exit"}:
            print("Gorusmek uzere.")
            return 0

        answer = ask_remote(server_url, text, web_mode, token)
        print(f"Asistan> {answer}")


def launch_gui_if_available() -> bool:
    gui_cmd = shutil.which("local-ai-bridge-chat")
    has_display = bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))
    if not (gui_cmd and has_display):
        return False
    subprocess.run([gui_cmd], check=False)
    return True


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="Fedora istemcisi: soruyu Windows AI host'a iletir."
    )
    parser.add_argument(
        "--server",
        default=os.getenv("AI_BRIDGE_SERVER", "ws://127.0.0.1:8000/ws/chat"),
        help="Windows makinedeki WS endpoint",
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Web modu acik: guncel bilgi icin internet aracini zorlar",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("AI_BRIDGE_TOKEN", ""),
        help="Sunucu token (AI_BRIDGE_TOKEN ile ayni olmali)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Terminalde interaktif sohbet modu",
    )
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Prompt verilmediginde GUI yerine terminal sohbeti ac",
    )
    parser.add_argument("prompt", nargs="*", help="Sorulacak metin")
    args = parser.parse_args()

    text = " ".join(args.prompt).strip()
    if not text and not args.interactive and not args.no_gui and launch_gui_if_available():
        return 0

    if args.interactive or not text:
        return run_interactive_chat(args.server, args.web, args.token)

    answer = ask_remote(args.server, text, args.web, args.token)
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


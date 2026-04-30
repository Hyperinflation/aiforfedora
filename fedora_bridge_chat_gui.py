#!/usr/bin/env python3

"""
Desktop chat UI for Fedora-side Local AI Bridge.
"""

import json
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

from websocket import create_connection


CONFIG_DIR = Path.home() / ".config" / "local-ai-bridge"
CONFIG_FILE = CONFIG_DIR / "config.json"
DEFAULT_SERVER = "ws://127.0.0.1:8000/ws/chat"


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


def load_config() -> dict:
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_config(server: str, token: str, web_mode: bool) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(
            {
                "server": server,
                "token": token,
                "web_mode": web_mode,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


class ChatApp:
    def __init__(self) -> None:
        env_server = os.getenv("AI_BRIDGE_SERVER", DEFAULT_SERVER)
        env_token = os.getenv("AI_BRIDGE_TOKEN", "")
        cfg = load_config()

        self.root = tk.Tk()
        self.root.title("Local AI Bridge")
        self.root.geometry("700x600")

        top = tk.Frame(self.root)
        top.pack(fill=tk.X, padx=10, pady=8)

        tk.Label(top, text="Server:").grid(row=0, column=0, sticky="w")
        self.server_var = tk.StringVar(value=cfg.get("server", env_server))
        tk.Entry(top, textvariable=self.server_var, width=52).grid(
            row=0, column=1, sticky="we", padx=6
        )

        tk.Label(top, text="Token:").grid(row=1, column=0, sticky="w")
        self.token_var = tk.StringVar(value=cfg.get("token", env_token))
        tk.Entry(top, textvariable=self.token_var, show="*", width=52).grid(
            row=1, column=1, sticky="we", padx=6
        )

        self.web_var = tk.BooleanVar(value=bool(cfg.get("web_mode", False)))
        tk.Checkbutton(top, text="Web modu", variable=self.web_var).grid(
            row=0, column=2, padx=4
        )

        tk.Button(top, text="Kaydet", command=self.on_save).grid(row=1, column=2, padx=4)
        top.columnconfigure(1, weight=1)

        self.chat = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state=tk.DISABLED)
        self.chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 8))

        bottom = tk.Frame(self.root)
        bottom.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.input_var = tk.StringVar()
        entry = tk.Entry(bottom, textvariable=self.input_var)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.bind("<Return>", self.on_send)

        self.send_btn = tk.Button(bottom, text="Gonder", command=self.on_send)
        self.send_btn.pack(side=tk.LEFT, padx=8)

        self._append("Sistem", "Hazir. Mesaj yazabilirsin.")
        entry.focus_set()

    def _append(self, who: str, text: str) -> None:
        self.chat.configure(state=tk.NORMAL)
        self.chat.insert(tk.END, f"{who}: {text}\n")
        self.chat.configure(state=tk.DISABLED)
        self.chat.see(tk.END)

    def on_save(self) -> None:
        save_config(
            self.server_var.get().strip(),
            self.token_var.get().strip(),
            self.web_var.get(),
        )
        messagebox.showinfo("Local AI Bridge", "Ayarlar kaydedildi.")

    def on_send(self, _event=None) -> None:
        text = self.input_var.get().strip()
        if not text:
            return
        self.input_var.set("")
        self._append("Sen", text)
        self.send_btn.configure(state=tk.DISABLED)
        threading.Thread(target=self._send_worker, args=(text,), daemon=True).start()

    def _send_worker(self, text: str) -> None:
        server = self.server_var.get().strip()
        token = self.token_var.get().strip()
        web_mode = self.web_var.get()
        try:
            answer = ask_remote(server, text, web_mode, token)
            self.root.after(0, lambda: self._append("Asistan", answer))
        except Exception as exc:  # broad by design for user-facing diagnostics
            self.root.after(0, lambda: self._append("Hata", str(exc)))
        finally:
            self.root.after(0, lambda: self.send_btn.configure(state=tk.NORMAL))

    def run(self) -> None:
        self.root.mainloop()


def main() -> int:
    ChatApp().run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

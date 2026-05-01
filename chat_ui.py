"""
Minimal rectangular chat box UI.
"""

import queue
import threading
import tkinter as tk

from agent import LocalAssistantAgent
from config import Settings


class ChatApp:
    def __init__(self) -> None:
        self.agent = LocalAssistantAgent(Settings())
        self.response_queue: queue.Queue[str] = queue.Queue()
        self.is_busy = False
        self.web_mode_active = False

        self.root = tk.Tk()
        self.root.title("AI Chat")
        self.root.geometry("200x500")
        self.root.minsize(200, 500)
        self.root.maxsize(260, 900)
        self.root.configure(bg="#f2f2f2")

        top_bar = tk.Frame(self.root, bg="#f2f2f2")
        top_bar.pack(fill="x", padx=6, pady=(6, 2))

        self.web_button = tk.Button(
            top_bar,
            text="🌐 Web",
            command=self._toggle_web_mode,
            bg="#ffffff",
            fg="#1f2a36",
            relief="solid",
            bd=1,
            font=("Segoe UI", 9, "bold"),
            padx=8,
            pady=3,
            cursor="hand2",
        )
        self.web_button.pack(side="left")
        self._update_web_button_style()

        self.chat_box = tk.Text(
            self.root,
            wrap="word",
            bg="#ffffff",
            fg="#111111",
            relief="solid",
            bd=1,
            font=("Segoe UI", 9),
            padx=6,
            pady=6,
        )
        self.chat_box.pack(fill="both", expand=True, padx=6, pady=(6, 4))
        self.chat_box.config(state="disabled")

        self.entry = tk.Entry(
            self.root,
            relief="solid",
            bd=1,
            font=("Segoe UI", 9),
        )
        self.entry.pack(fill="x", padx=6, pady=(0, 6))
        self.entry.bind("<Return>", self._on_enter)

        self._insert_message("Asistan", "Hazir.")
        self.root.after(120, self._poll_responses)

    def _toggle_web_mode(self) -> None:
        self.web_mode_active = not self.web_mode_active
        self._update_web_button_style()
        if self.web_mode_active:
            self._insert_message("Sistem", "Web modu aktif: aramalar internetten yapilacak.")
        else:
            self._insert_message("Sistem", "Web modu kapali: yerel bilgi modu.")

    def _update_web_button_style(self) -> None:
        if self.web_mode_active:
            self.web_button.config(
                bg="#eaf3ff",
                fg="#0f4da8",
                bd=2,
                highlightthickness=2,
                highlightbackground="#2f80ff",
                highlightcolor="#2f80ff",
            )
        else:
            self.web_button.config(
                bg="#ffffff",
                fg="#1f2a36",
                bd=1,
                highlightthickness=1,
                highlightbackground="#bfc7d4",
                highlightcolor="#bfc7d4",
            )

    def _insert_message(self, role: str, content: str) -> None:
        self.chat_box.config(state="normal")
        self.chat_box.insert("end", f"{role}: {content}\n\n")
        self.chat_box.see("end")
        self.chat_box.config(state="disabled")

    def _on_enter(self, _: tk.Event) -> str:
        self.send_message()
        return "break"

    def send_message(self) -> None:
        if self.is_busy:
            return

        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.entry.delete(0, "end")
        self._insert_message("Sen", user_text)
        self.is_busy = True

        thread = threading.Thread(
            target=self._generate_response_worker, args=(user_text,), daemon=True
        )
        thread.start()

    def _generate_response_worker(self, user_text: str) -> None:
        try:
            answer = self.agent.handle(
                user_text,
                force_web=self.web_mode_active,
                disable_web=not self.web_mode_active,
            )
        except Exception as exc:  # noqa: BLE001
            answer = f"Hata: {exc}"
        self.response_queue.put(answer)

    def _poll_responses(self) -> None:
        try:
            while True:
                response = self.response_queue.get_nowait()
                self._insert_message("Asistan", response)
                self.is_busy = False
        except queue.Empty:
            pass
        self.root.after(120, self._poll_responses)

    def run(self) -> None:
        self.root.mainloop()


if __name__ == "__main__":
    ChatApp().run()


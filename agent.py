"""
Agent orchestration and LLM-based tool routing.
"""

import json
from typing import Dict, List

from config import Settings
from llm import OllamaClient
from memory import ChatMemory
from rag import LocalRAG
from tools.coding_tool import CodingTool
from tools.terminal_tool import TerminalConfig, TerminalTool
from tools.web_tool import WebTool


class LocalAssistantAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = OllamaClient(settings)
        self.memory = ChatMemory(
            history_file=settings.history_file,
            max_messages=settings.max_history_messages,
        )
        self.rag = LocalRAG(settings.docs_path)
        self.terminal = TerminalTool(
            TerminalConfig(
                allowed_commands=settings.allowed_commands,
                blocked_patterns=settings.blocked_patterns,
            )
        )
        self.web = WebTool()
        self.coder = CodingTool(self.llm)

    def _should_force_web(self, user_input: str) -> bool:
        text = user_input.lower()
        web_triggers = [
            "en guncel",
            "guncel",
            "son surum",
            "latest",
            "current",
            "su an",
            "today",
            "bu ay",
            "bu yil",
            "release date",
            "ne zaman cikti",
            "haber",
            "fiyat",
            "kur",
        ]
        return any(token in text for token in web_triggers)

    def _tool_router(self, user_input: str) -> Dict[str, str]:
        router_prompt = (
            "Kullanici istegini analiz et ve en uygun araci sec.\n"
            "Araclar:\n"
            "1) terminal: Linux terminal komutlari\n"
            "2) web: internet arama ve ozet\n"
            "3) coding: Python kod yazma/duzeltme\n"
            "4) chat: genel sohbet/aciklama\n\n"
            "JSON don: {\"tool\":\"...\", \"tool_input\":\"...\"}\n"
            "Sadece gecerli JSON don."
        )
        response = self.llm.chat(
            [
                {"role": "system", "content": router_prompt},
                {"role": "user", "content": user_input},
            ]
        )
        try:
            data = json.loads(response)
            tool = data.get("tool", "chat")
            tool_input = data.get("tool_input", user_input)
            if tool not in {"terminal", "web", "coding", "chat"}:
                tool = "chat"
            return {"tool": tool, "tool_input": tool_input}
        except json.JSONDecodeError:
            return {"tool": "chat", "tool_input": user_input}

    def _build_assistant_prompt(
        self,
        user_input: str,
        tool_result: str,
        memory_messages: List[Dict[str, str]],
        selected_tool: str,
    ) -> List[Dict[str, str]]:
        chunks = self.rag.retrieve(user_input, top_k=self.settings.rag_top_k)
        rag_context = "\n\n".join(
            [f"Kaynak: {chunk.source}\nIcerik:\n{chunk.text}" for chunk in chunks]
        )
        if not rag_context:
            rag_context = "Yok"

        system_text = (
            "Sen yerel bir AI asistansin. Turkce cevap ver. "
            "Arac ciktilarini kullanarak net ve kisa yanit ver. "
            "Eger secili arac web ise, cevabi oncelikle WEB sonucuna dayandir ve "
            "emin degilsen bunu acikca belirt."
        )
        context_text = (
            f"SELECTED_TOOL: {selected_tool}\n\n"
            f"TOOL_RESULT:\n{tool_result}\n\n"
            f"RAG_CONTEXT:\n{rag_context}\n"
        )
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_text}]
        messages.extend(memory_messages[-10:])
        messages.append({"role": "system", "content": context_text})
        messages.append({"role": "user", "content": user_input})
        return messages

    def handle(
        self, user_input: str, force_web: bool = False, disable_web: bool = False
    ) -> str:
        memory_messages = self.memory.load()
        decision = self._tool_router(user_input)
        tool = decision["tool"]
        tool_input = decision["tool_input"]

        if force_web:
            tool = "web"
            tool_input = user_input
        elif disable_web:
            # In local-only mode, avoid internet tool.
            if tool == "web":
                tool = "chat"
                tool_input = user_input
        # Hard filter: force online lookup for time-sensitive queries.
        elif self._should_force_web(user_input):
            tool = "web"
            tool_input = user_input

        if tool == "terminal":
            tool_result = self.terminal.run(tool_input)
        elif tool == "web":
            tool_result = self.web.search_and_summarize(tool_input)
        elif tool == "coding":
            tool_result = self.coder.solve(tool_input)
        else:
            tool_result = "Arac cagrisi yapilmadi."

        messages = self._build_assistant_prompt(
            user_input, tool_result, memory_messages, tool
        )
        answer = self.llm.chat(messages)

        memory_messages.append({"role": "user", "content": user_input})
        memory_messages.append({"role": "assistant", "content": answer})
        self.memory.save(memory_messages)

        return answer


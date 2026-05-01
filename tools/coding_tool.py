"""
Coding helper for Python scripts.
"""

from llm import OllamaClient


class CodingTool:
    def __init__(self, llm: OllamaClient):
        self.llm = llm

    def solve(self, prompt: str) -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Sen uzman bir Python coding asistansin. "
                    "Temiz ve calisir kod uret, gerekli yerlerde kisa aciklama ver."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        return self.llm.chat(messages)


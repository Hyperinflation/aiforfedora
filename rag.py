"""
Very small local-file RAG helper.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class Chunk:
    source: str
    text: str


class LocalRAG:
    def __init__(self, docs_path: Path):
        self.docs_path = docs_path
        self.docs_path.mkdir(parents=True, exist_ok=True)

    def _token_overlap_score(self, query: str, text: str) -> int:
        q_tokens = {t.lower() for t in query.split() if t.strip()}
        t_tokens = {t.lower() for t in text.split() if t.strip()}
        return len(q_tokens.intersection(t_tokens))

    def _iter_text_files(self) -> List[Path]:
        files: List[Path] = []
        for ext in ("*.txt", "*.md", "*.py", "*.json"):
            files.extend(self.docs_path.rglob(ext))
        return files

    def retrieve(self, query: str, top_k: int = 3) -> List[Chunk]:
        scored: List[Tuple[int, Chunk]] = []
        for file in self._iter_text_files():
            try:
                content = file.read_text(encoding="utf-8", errors="ignore")
            except Exception:  # noqa: BLE001
                continue
            score = self._token_overlap_score(query, content)
            if score > 0:
                scored.append((score, Chunk(source=str(file), text=content[:1200])))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored[:top_k]]


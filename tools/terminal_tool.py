"""
Safe terminal execution tool.
"""

import shlex
import subprocess
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class TerminalConfig:
    allowed_commands: List[str]
    blocked_patterns: List[str]


class TerminalTool:
    def __init__(self, config: TerminalConfig):
        self.config = config

    def _is_safe(self, command: str) -> Tuple[bool, str]:
        normalized = command.strip().lower()
        for bad in self.config.blocked_patterns:
            if bad in normalized:
                return False, f"Engellendi: tehlikeli ifade bulundu ({bad})"

        if not normalized:
            return False, "Komut bos."

        try:
            parts = shlex.split(command)
        except ValueError:
            return False, "Komut parse edilemedi."

        root_cmd = parts[0]
        if root_cmd not in self.config.allowed_commands:
            return False, f"Komut beyaz listede degil: {root_cmd}"

        return True, ""

    def run(self, command: str) -> str:
        ok, reason = self._is_safe(command)
        if not ok:
            return f"[TerminalTool] Reddedildi: {reason}"

        try:
            result = subprocess.run(
                command,
                shell=True,
                check=False,
                capture_output=True,
                text=True,
                timeout=20,
            )
            stdout = result.stdout.strip()
            stderr = result.stderr.strip()
            return (
                f"[TerminalTool] exit={result.returncode}\n"
                f"STDOUT:\n{stdout or '(bos)'}\n\n"
                f"STDERR:\n{stderr or '(bos)'}"
            )
        except subprocess.TimeoutExpired:
            return "[TerminalTool] Zaman asimi: komut 20 saniyeyi asti."


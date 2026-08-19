from __future__ import annotations


class MessageTool:
    def build_text(self, *, title: str, message: str) -> str:
        return f"{title}\n{message}"

from __future__ import annotations

from typing import Any

from app.tools.supabase_tool import SupabaseTool


class LoggingAgent:
    def __init__(self, supabase_tool: SupabaseTool) -> None:
        self._supabase_tool = supabase_tool

    def log(self, *, user_id: str, reminder_id: str, status: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        print(f"[logging] status={status} reminder_id={reminder_id}")
        return self._supabase_tool.save_log(
            user_id=user_id,
            reminder_id=reminder_id,
            status=status,
            metadata=metadata,
        )


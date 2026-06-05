from __future__ import annotations

from app.models import AnalyticsResponse
from app.tools.supabase_tool import SupabaseTool


class AnalyticsAgent:
    def __init__(self, supabase_tool: SupabaseTool) -> None:
        self._supabase_tool = supabase_tool

    def summarize(self) -> AnalyticsResponse:
        logs = self._supabase_tool.list_logs()
        done = sum(1 for log in logs if log["status"] == "done")
        not_done = sum(1 for log in logs if log["status"] == "not_done")
        postponed = sum(1 for log in logs if log["status"] == "postponed")
        total = done + not_done + postponed
        completion_rate = (done / total * 100.0) if total else 0.0
        return AnalyticsResponse(
            total=total,
            done=done,
            not_done=not_done,
            postponed=postponed,
            completion_rate=round(completion_rate, 2),
        )


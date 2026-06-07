from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from app.models import (
    AnalyticsResponse,
    DashboardActivityMetric,
    DashboardMetricsResponse,
    DashboardRecentLog,
    DashboardSummary,
)
from app.tools.supabase_tool import SupabaseTool
from app.tools.time_tool import TimeTool


class AnalyticsAgent:
    DEFAULT_ACTIVITIES = [
        "Peitoral",
        "Costas",
        "Pernas",
        "Ombros",
        "Bracos",
        "Caminhada",
    ]

    def __init__(self, supabase_tool: SupabaseTool, time_tool: TimeTool) -> None:
        self._supabase_tool = supabase_tool
        self._time_tool = time_tool

    def summarize(self) -> AnalyticsResponse:
        summary = self.get_summary_metrics()
        return AnalyticsResponse(
            total=summary.total_answered,
            done=summary.done,
            not_done=summary.not_done,
            postponed=summary.postponed,
            completion_rate=summary.completion_rate,
        )

    def get_dashboard_metrics(self) -> DashboardMetricsResponse:
        reminders = self._supabase_tool.list_reminders()
        logs = self._supabase_tool.list_logs()
        reminder_map = {str(reminder["id"]): reminder for reminder in reminders}
        return DashboardMetricsResponse(
            summary=self.get_summary_metrics(logs),
            activities=self.get_activity_metrics(logs, reminder_map),
            recent_logs=self.get_recent_logs(logs, reminder_map),
        )

    def get_summary_metrics(self, logs: list[dict] | None = None) -> DashboardSummary:
        entries = logs if logs is not None else self._supabase_tool.list_logs()
        done = sum(1 for log in entries if log.get("status") == "done")
        not_done = sum(1 for log in entries if log.get("status") == "not_done")
        postponed = sum(1 for log in entries if log.get("status") == "postponed")
        total_answered = done + not_done + postponed
        completion_rate = (done / total_answered * 100.0) if total_answered else 0.0
        return DashboardSummary(
            total_answered=total_answered,
            done=done,
            not_done=not_done,
            postponed=postponed,
            completion_rate=round(completion_rate, 2),
        )

    def get_activity_metrics(
        self,
        logs: list[dict] | None = None,
        reminder_map: dict[str, dict] | None = None,
    ) -> list[DashboardActivityMetric]:
        entries = logs if logs is not None else self._supabase_tool.list_logs()
        reminders = reminder_map or {
            str(reminder["id"]): reminder for reminder in self._supabase_tool.list_reminders()
        }
        grouped: dict[str, dict[str, int]] = defaultdict(
            lambda: {"sent": 0, "done": 0, "not_done": 0, "postponed": 0, "error": 0}
        )

        for activity in self.DEFAULT_ACTIVITIES:
            grouped[activity]

        for log in entries:
            reminder = reminders.get(str(log.get("reminder_id")))
            title = self._derive_activity_title(reminder)
            status = str(log.get("status", ""))
            if status in grouped[title]:
                grouped[title][status] += 1

        metrics: list[DashboardActivityMetric] = []
        extra_titles = sorted(
            title for title in grouped.keys() if title not in self.DEFAULT_ACTIVITIES
        )
        for title in [*self.DEFAULT_ACTIVITIES, *extra_titles]:
            counts = grouped[title]
            total_answered = counts["done"] + counts["not_done"] + counts["postponed"]
            completion_rate = (counts["done"] / total_answered * 100.0) if total_answered else 0.0
            metrics.append(
                DashboardActivityMetric(
                    title=title,
                    sent=counts["sent"],
                    done=counts["done"],
                    not_done=counts["not_done"],
                    postponed=counts["postponed"],
                    error=counts["error"],
                    completion_rate=round(completion_rate, 2),
                )
            )
        return metrics

    def get_recent_logs(
        self,
        logs: list[dict] | None = None,
        reminder_map: dict[str, dict] | None = None,
        limit: int = 12,
    ) -> list[DashboardRecentLog]:
        entries = logs if logs is not None else self._supabase_tool.list_logs()
        reminders = reminder_map or {
            str(reminder["id"]): reminder for reminder in self._supabase_tool.list_reminders()
        }
        sorted_logs = sorted(entries, key=lambda log: str(log.get("created_at", "")), reverse=True)
        recent: list[DashboardRecentLog] = []
        for log in sorted_logs[:limit]:
            reminder = reminders.get(str(log.get("reminder_id")), {})
            recent.append(
                DashboardRecentLog(
                    title=str(reminder.get("title", "Sem atividade")),
                    status=str(log.get("status", "")),
                    created_at=self._format_datetime(log.get("created_at")),
                    message=str(reminder.get("message", "")),
                )
            )
        return recent

    def _derive_activity_title(self, reminder: dict | None) -> str:
        title = str((reminder or {}).get("title", "")).strip()
        normalized = title.casefold()
        activity_map = {
            "peitoral": "Peitoral",
            "costas": "Costas",
            "pernas": "Pernas",
            "ombros": "Ombros",
            "bracos": "Bracos",
            "braços": "Bracos",
            "caminhada": "Caminhada",
        }
        for key, value in activity_map.items():
            if key in normalized:
                return value
        return title or "Outros"

    def _format_datetime(self, value: object) -> str:
        if not value:
            return ""
        created_at = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        current_tz = self._time_tool.now().tzinfo
        if current_tz is None:
            return created_at.isoformat()
        return created_at.astimezone(current_tz).isoformat()

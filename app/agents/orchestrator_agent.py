from __future__ import annotations

from app.agents.logging_agent import LoggingAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.reminder_agent import ReminderAgent


class OrchestratorAgent:
    def __init__(
        self,
        reminder_agent: ReminderAgent,
        notification_agent: NotificationAgent,
        logging_agent: LoggingAgent,
    ) -> None:
        self._reminder_agent = reminder_agent
        self._notification_agent = notification_agent
        self._logging_agent = logging_agent

    async def run_due_reminders(self, window_minutes: int = 5) -> list[str]:
        sent_keys: list[str] = []
        current = self._reminder_agent._time_tool.now()
        window_start, window_end = self._reminder_agent._time_tool.window_bounds(
            window_minutes, current=current
        )
        for dispatch in self._reminder_agent.due_reminders(window_minutes=window_minutes):
            if self._logging_agent._supabase_tool.has_sent_log_in_window(
                reminder_id=str(dispatch.reminder_id),
                window_start=window_start,
                window_end=window_end,
            ):
                continue
            try:
                await self._notification_agent.notify(dispatch)
                self._logging_agent.log(
                    user_id=str(dispatch.user_id),
                    reminder_id=str(dispatch.reminder_id),
                    status="sent",
                )
                sent_keys.append(dispatch.dedupe_key)
            except Exception as exc:  # pragma: no cover - defensive logging
                self._logging_agent.log(
                    user_id=str(dispatch.user_id),
                    reminder_id=str(dispatch.reminder_id),
                    status="error",
                    metadata={"detail": str(exc)},
                )
        return sent_keys

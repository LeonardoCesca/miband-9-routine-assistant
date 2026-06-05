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

    async def run_due_reminders(self, processed_keys: set[str]) -> list[str]:
        sent_keys: list[str] = []
        for dispatch in self._reminder_agent.due_reminders():
            if dispatch.dedupe_key in processed_keys:
                continue
            try:
                await self._notification_agent.notify(dispatch)
                self._logging_agent.log(
                    user_id=str(dispatch.user_id),
                    reminder_id=str(dispatch.reminder_id),
                    status="sent",
                )
                processed_keys.add(dispatch.dedupe_key)
                sent_keys.append(dispatch.dedupe_key)
            except Exception as exc:  # pragma: no cover - defensive logging
                self._logging_agent.log(
                    user_id=str(dispatch.user_id),
                    reminder_id=str(dispatch.reminder_id),
                    status="error",
                    metadata={"detail": str(exc)},
                )
        return sent_keys


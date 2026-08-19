from __future__ import annotations

from app.models import ReminderDispatch
from app.notifications.service import NotificationService


class NotificationAgent:
    def __init__(self, notification_service: NotificationService) -> None:
        self._service = notification_service

    async def notify(self, dispatch: ReminderDispatch) -> dict:
        await self._service.send(
            title=dispatch.title,
            message=dispatch.message,
        )
        return {"ok": True}

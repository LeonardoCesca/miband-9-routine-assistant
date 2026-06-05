from __future__ import annotations

from typing import Any

from app.models import ReminderLogRead
from app.services.supabase_service import SupabaseService


class SupabaseToolError(Exception):
    pass


class SupabaseTool:
    def __init__(self, service: SupabaseService) -> None:
        self._service = service

    def create_user(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._service.insert("users", payload)

    def list_users(self) -> list[dict[str, Any]]:
        return self._service.select("users")

    def create_reminder(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._service.insert("reminders", payload)

    def list_reminders(self) -> list[dict[str, Any]]:
        return self._service.select("reminders")

    def list_active_reminders(self) -> list[dict[str, Any]]:
        return self._service.select("reminders", filters={"active": True})

    def get_reminder(self, reminder_id: str) -> dict[str, Any] | None:
        rows = self._service.select("reminders", filters={"id": reminder_id})
        return rows[0] if rows else None

    def toggle_reminder(self, reminder_id: str) -> dict[str, Any]:
        reminder = self.get_reminder(reminder_id)
        if reminder is None:
            raise SupabaseToolError("Reminder not found")
        updated = self._service.update(
            "reminders",
            filters={"id": reminder_id},
            payload={"active": not bool(reminder["active"])},
        )
        return updated[0] if updated else {**reminder, "active": not bool(reminder["active"])}

    def save_log(
        self,
        *,
        user_id: str,
        reminder_id: str,
        status: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        payload = ReminderLogRead(
            user_id=user_id,
            reminder_id=reminder_id,
            status=status,
            metadata=metadata or {},
        ).model_dump(mode="json", exclude_none=True)
        return self._service.insert("reminder_logs", payload)

    def list_logs(self) -> list[dict[str, Any]]:
        return self._service.select("reminder_logs")


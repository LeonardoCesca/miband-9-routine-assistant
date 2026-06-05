from __future__ import annotations

from typing import Any

from app.models import ReminderDispatch
from app.tools.message_tool import MessageTool
from app.tools.supabase_tool import SupabaseTool
from app.tools.time_tool import TimeTool


class ReminderAgent:
    def __init__(
        self,
        supabase_tool: SupabaseTool,
        message_tool: MessageTool,
        time_tool: TimeTool,
    ) -> None:
        self._supabase_tool = supabase_tool
        self._message_tool = message_tool
        self._time_tool = time_tool

    def due_reminders(self) -> list[ReminderDispatch]:
        active_reminders = self._supabase_tool.list_active_reminders()
        users = {user["id"]: user for user in self._supabase_tool.list_users()}
        current = self._time_tool.now()
        due: list[ReminderDispatch] = []

        for reminder in active_reminders:
            if not self._time_tool.matches_minute(
                hour=int(reminder["hour"]),
                minute=int(reminder["minute"]),
                current=current,
            ):
                continue

            user = users.get(reminder["user_id"])
            if not user:
                continue

            reminder_id = str(reminder["id"])
            due.append(
                ReminderDispatch(
                    reminder_id=reminder["id"],
                    user_id=reminder["user_id"],
                    chat_id=user["telegram_chat_id"],
                    title=reminder["title"],
                    message=reminder["message"],
                    text=self._message_tool.build_text(
                        title=reminder["title"],
                        message=reminder["message"],
                    ),
                    reply_markup=self._message_tool.build_keyboard(reminder_id),
                    dedupe_key=self._time_tool.build_minute_key(reminder_id, current=current),
                )
            )
        return due


from __future__ import annotations

from app.models import ReminderDispatch, TelegramSendMessagePayload
from app.tools.telegram_tool import TelegramTool


class NotificationAgent:
    def __init__(self, telegram_tool: TelegramTool) -> None:
        self._telegram_tool = telegram_tool

    async def notify(self, dispatch: ReminderDispatch) -> dict:
        payload = TelegramSendMessagePayload(
            chat_id=dispatch.chat_id,
            text=dispatch.text,
            reply_markup=dispatch.reply_markup,
        )
        return await self._telegram_tool.send_message(payload)

    async def answer_callback(self, callback_query_id: str, text: str) -> dict:
        return await self._telegram_tool.answer_callback_query(callback_query_id, text)


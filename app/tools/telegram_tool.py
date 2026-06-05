from __future__ import annotations

from typing import Any

from app.models import TelegramSendMessagePayload
from app.services.telegram_service import TelegramService, TelegramServiceError


class TelegramToolError(Exception):
    pass


class TelegramTool:
    def __init__(self, service: TelegramService) -> None:
        self._service = service

    async def send_message(self, payload: TelegramSendMessagePayload) -> dict[str, Any]:
        try:
            return await self._service.post(
                "sendMessage",
                {
                    "chat_id": payload.chat_id,
                    "text": payload.text,
                    "parse_mode": "Markdown",
                    "reply_markup": payload.reply_markup.model_dump(mode="json"),
                },
            )
        except TelegramServiceError as exc:
            raise TelegramToolError("Failed to send Telegram message") from exc

    async def answer_callback_query(self, callback_query_id: str, text: str) -> dict[str, Any]:
        try:
            return await self._service.post(
                "answerCallbackQuery",
                {"callback_query_id": callback_query_id, "text": text},
            )
        except TelegramServiceError as exc:
            raise TelegramToolError("Failed to answer Telegram callback query") from exc


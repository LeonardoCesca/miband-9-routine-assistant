from __future__ import annotations

from typing import Any

import httpx


class TelegramServiceError(Exception):
    pass


class TelegramService:
    def __init__(self, bot_token: str, timeout: float = 10.0) -> None:
        self._bot_token = bot_token
        self._timeout = timeout

    @property
    def base_url(self) -> str:
        return f"https://api.telegram.org/bot{self._bot_token}"

    async def post(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.base_url}/{method}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.post(url, json=payload)
        if response.status_code >= 400:
            raise TelegramServiceError(
                f"Telegram API returned status {response.status_code}"
            )
        data = response.json()
        if not data.get("ok", False):
            raise TelegramServiceError("Telegram API returned an unsuccessful result")
        return data


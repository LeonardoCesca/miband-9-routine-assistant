from __future__ import annotations

from app.notifications.transport import NotificationTransport


class NotificationService:
    def __init__(self, transport: NotificationTransport) -> None:
        self._transport = transport

    async def connect(self) -> None:
        await self._transport.connect()

    async def disconnect(self) -> None:
        await self._transport.disconnect()

    async def send(self, title: str, message: str) -> None:
        await self._transport.send(title, message)

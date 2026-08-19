from __future__ import annotations

from abc import ABC, abstractmethod


class NotificationTransport(ABC):
    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def send(self, title: str, message: str) -> None:
        ...

from __future__ import annotations

import logging

from app.miband.client import MiBandClient
from app.miband.models import (
    BandAuthError,
    BandConnectionError,
    BandConnectionTimeout,
    BandState,
)

logger = logging.getLogger(__name__)

MAX_RECONNECT_ATTEMPTS = 3


class ConnectionManager:
    def __init__(self, address: str, timeout: float = 10.0) -> None:
        self._address = address
        self._timeout = timeout
        self._client = MiBandClient(address)

    @property
    def client(self) -> MiBandClient:
        return self._client

    @property
    def state(self) -> BandState:
        return self._client.state

    async def connect(self) -> None:
        try:
            await self._client.connect(timeout=self._timeout)
        except BandConnectionError as exc:
            raise BandConnectionTimeout(str(exc)) from exc

    async def disconnect(self) -> None:
        await self._client.disconnect()

    async def reconnect(self) -> None:
        for attempt in range(1, MAX_RECONNECT_ATTEMPTS + 1):
            logger.info("[BLE] Reconnect attempt %d/%d", attempt, MAX_RECONNECT_ATTEMPTS)
            try:
                await self._client.disconnect()
                await self.connect()
                logger.info("[BLE] Reconnected successfully")
                return
            except (BandConnectionError, BandConnectionTimeout):
                continue
        raise BandConnectionError(
            "Failed to reconnect after maximum attempts"
        )

    async def ensure_connected(self) -> None:
        if not self._client.is_connected:
            logger.info("[BLE] Connection lost, reconnecting...")
            await self.reconnect()

from __future__ import annotations

import logging

from app.config import Settings
from app.miband.connection import ConnectionManager
from app.miband.models import BandState, Notification
from app.miband.protocol import MiBandProtocol
from app.miband.scanner import find_miband
from app.notifications.transport import NotificationTransport

logger = logging.getLogger(__name__)


class BLETransport(NotificationTransport):
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._connection: ConnectionManager | None = None
        self._protocol: MiBandProtocol | None = None

    async def connect(self) -> None:
        logger.info("[BLE] Scanning for Mi Band...")
        device = await find_miband(timeout=10.0)
        logger.info("[BLE] Mi Band found: %s (%s)", device.name, device.address)

        self._connection = ConnectionManager(device.address)
        await self._connection.connect()

        self._protocol = MiBandProtocol(self._connection.client)
        await self._protocol.authenticate()

        logger.info("[BLE] READY")

    async def disconnect(self) -> None:
        if self._connection:
            await self._connection.disconnect()
            self._connection = None
            self._protocol = None

    async def send(self, title: str, message: str) -> None:
        if not self._connection or not self._protocol:
            raise RuntimeError("BLE not connected. Call connect() first.")

        if self._connection.state != BandState.READY:
            logger.info("[BLE] Not in READY state, reconnecting...")
            await self.connect()

        notification = Notification(title=title, message=message)
        await self._protocol.send_notification(notification)

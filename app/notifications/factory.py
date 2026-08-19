from __future__ import annotations

from app.config import Settings
from app.notifications.ble import BLETransport
from app.notifications.transport import NotificationTransport


def create_transport(settings: Settings) -> NotificationTransport:
    return BLETransport(settings)

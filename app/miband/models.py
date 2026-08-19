from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class BandState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATING = "authenticating"
    READY = "ready"
    ERROR = "error"


class BLEError(Exception):
    pass


class BandUnavailableError(BLEError):
    pass


class BandConnectionError(BLEError):
    pass


class BandDiscoveryTimeout(BLEError):
    pass


class BandConnectionTimeout(BLEError):
    pass


class BandAuthError(BLEError):
    pass


class BandWriteTimeout(BLEError):
    pass


@dataclass
class Notification:
    title: str
    message: str

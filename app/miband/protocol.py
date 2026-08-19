from __future__ import annotations

import logging

from app.miband.client import MiBandClient
from app.miband.models import BandAuthError, BandState, Notification

logger = logging.getLogger(__name__)

# These UUIDs MUST be discovered via GATT inspection on the actual Mi Band 9 Pro.
# Do NOT copy from older Mi Band models.
# Replace after running: python -m app.miband.inspect
AUTH_CHAR_UUID: str = ""
NOTIFY_CHAR_UUID: str = ""
AUTH_SERVICE_UUID: str = ""
NOTIFY_SERVICE_UUID: str = ""

# Header bytes for notification commands — discover via GATT inspection
NOTIFICATION_CMD_HEADER: bytes = b""


class MiBandProtocol:
    def __init__(self, client: MiBandClient) -> None:
        self._client = client

    async def authenticate(self) -> None:
        if not AUTH_CHAR_UUID or not AUTH_SERVICE_UUID:
            logger.warning("[BLE] Auth UUIDs not configured. Skipping authentication.")
            self._client.set_state(BandState.READY)
            return

        logger.info("[BLE] Authenticating")
        self._client.set_state(BandState.AUTHENTICATING)

        try:
            # Authentication flow — implement after GATT inspection
            # Step 1: Read auth characteristic
            # Step 2: Send auth challenge/response
            # Step 3: Verify auth success
            #
            # Placeholder — replace with actual protocol after inspection
            logger.info("[BLE] Auth flow placeholder — needs GATT inspection data")
            self._client.set_state(BandState.READY)
            logger.info("[BLE] Authenticated (placeholder)")
        except Exception as exc:
            self._client.set_state(BandState.ERROR)
            raise BandAuthError(f"Authentication failed: {exc}") from exc

    async def send_notification(self, notification: Notification) -> None:
        if self._client.state != BandState.READY:
            raise BandAuthError("Cannot send: not in READY state")

        from app.miband.notification import encode_notification

        payload = encode_notification(notification)

        if not NOTIFY_CHAR_UUID:
            raise BandAuthError(
                "Notification characteristic UUID not configured. "
                "Run GATT inspection first."
            )

        logger.info("[BLE] Sending notification (%d bytes)", len(payload))
        await self._client.write(NOTIFY_CHAR_UUID, payload)
        logger.info("[BLE] Notification sent")

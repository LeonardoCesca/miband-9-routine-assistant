from __future__ import annotations

import logging

from app.miband.models import Notification

logger = logging.getLogger(__name__)

# Maximum payload size per BLE write — discovered via GATT inspection.
# Do NOT hardcode to 20 bytes. Use the actual MTU negotiated by BleakClient.
DEFAULT_MAX_PAYLOAD = 20


def encode_notification(notification: Notification) -> bytes:
    title_bytes = notification.title.encode("utf-8")
    message_bytes = notification.message.encode("utf-8")

    # Separator between title and message
    payload = title_bytes + b"\n" + message_bytes

    logger.debug(
        "[BLE] Encoded notification: title=%d bytes, message=%d bytes, total=%d bytes",
        len(title_bytes),
        len(message_bytes),
        len(payload),
    )
    return payload


def fragment_payload(payload: bytes, max_size: int = DEFAULT_MAX_PAYLOAD) -> list[bytes]:
    if max_size <= 0:
        raise ValueError("max_size must be positive")

    chunks: list[bytes] = []
    offset = 0
    while offset < len(payload):
        chunk = payload[offset : offset + max_size]
        chunks.append(chunk)
        offset += max_size

    if len(chunks) > 1:
        logger.debug("[BLE] Fragmented into %d chunks", len(chunks))

    return chunks

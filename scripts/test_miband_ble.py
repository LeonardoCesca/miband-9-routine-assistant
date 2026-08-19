from __future__ import annotations

import asyncio
import logging
import sys

from app.config import get_settings
from app.miband.connection import ConnectionManager
from app.miband.models import BandState, Notification
from app.miband.notification import encode_notification, fragment_payload
from app.miband.protocol import MiBandProtocol
from app.miband.scanner import find_miband


async def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        stream=sys.stdout,
    )

    print("Mi Band 9 Pro — BLE Test\n")

    # Step 1: Scan
    print("Scanning...")
    try:
        device = await find_miband(timeout=10.0)
    except Exception as exc:
        print(f"FAIL: {exc}")
        return
    print(f"PASS: Mi Band 9 Pro found ({device.address})\n")

    # Step 2: Connect
    print("Connecting...")
    conn = ConnectionManager(device.address)
    try:
        await conn.connect()
    except Exception as exc:
        print(f"FAIL: {exc}")
        return
    print("PASS: Connected\n")

    # Step 3: Authenticate
    print("Authenticating...")
    protocol = MiBandProtocol(conn.client)
    try:
        await protocol.authenticate()
    except Exception as exc:
        print(f"FAIL: {exc}")
        await conn.disconnect()
        return
    print("PASS: Authenticated\n")

    # Step 4: Ready
    if conn.state != BandState.READY:
        print(f"FAIL: State is {conn.state}, expected READY")
        await conn.disconnect()
        return
    print("PASS: READY\n")

    # Step 5: Send notification
    notification = Notification(
        title="MiBand Assistant",
        message="Conexao direta BLE funcionando.",
    )
    payload = encode_notification(notification)
    print(f"Payload ({len(payload)} bytes): {payload!r}")
    chunks = fragment_payload(payload, max_size=20)
    print(f"Chunks: {len(chunks)}")

    print("\nSending notification...")
    try:
        await protocol.send_notification(notification)
    except Exception as exc:
        print(f"FAIL: {exc}")
        await conn.disconnect()
        return
    print("PASS: Notification sent\n")

    # Cleanup
    await conn.disconnect()
    print("Done. Check your Mi Band 9 Pro.")


if __name__ == "__main__":
    asyncio.run(main())

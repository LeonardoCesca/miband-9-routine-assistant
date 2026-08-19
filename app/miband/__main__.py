from __future__ import annotations

import asyncio
import logging
import sys

from app.miband.scanner import scan_devices


async def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(message)s",
        stream=sys.stdout,
    )
    print("Scanning for BLE devices...\n")
    devices = await scan_devices(timeout=8.0)

    if not devices:
        print("No devices found.")
        return

    for i, dev in enumerate(devices, 1):
        print(f"[{i}]")
        print(f"  Name:    {dev.name}")
        print(f"  Address: {dev.address}")
        print(f"  RSSI:    {dev.rssi}")
        print()


if __name__ == "__main__":
    asyncio.run(main())

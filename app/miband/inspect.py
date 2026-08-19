from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path

from bleak import BleakClient

from app.config import get_settings
from app.miband.scanner import find_miband


async def inspect_gatt(address: str, output_path: str | None = None) -> dict:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.DEBUG, format="%(message)s", stream=sys.stdout)

    print(f"\nConnecting to {address}...\n")

    async with BleakClient(address, timeout=15.0) as client:
        if not client.is_connected:
            print("Failed to connect.")
            return {}

        print("Connected. Enumerating GATT...\n")

        result: dict = {
            "device": {
                "name": "",
                "address": address,
            },
            "services": [],
        }

        for service in client.services:
            service_data: dict = {
                "uuid": str(service.uuid),
                "description": service.description,
                "characteristics": [],
            }

            print("=" * 60)
            print(f"SERVICE")
            print(f"UUID: {service.uuid}")
            print(f"Description: {service.description}")
            print("=" * 60)

            for char in service.characteristics:
                props = [p.upper() for p in char.properties]
                char_data: dict = {
                    "uuid": str(char.uuid),
                    "description": char.description,
                    "properties": props,
                    "descriptors": [],
                }

                print(f"\nCharacteristic")
                print(f"UUID: {char.uuid}")
                print(f"Description: {char.description}")
                print(f"Properties:")
                for p in props:
                    print(f"  {p}")

                for desc in char.descriptors:
                    desc_data: dict = {
                        "uuid": str(desc.uuid),
                        "description": desc.description,
                    }
                    char_data["descriptors"].append(desc_data)
                    print(f"Descriptor: {desc.uuid} ({desc.description})")

                service_data["characteristics"].append(char_data)

            result["services"].append(service_data)
            print()

    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nGATT exported to: {output_path}")

    return result


async def main() -> None:
    settings = get_settings()
    output_path: str | None = None

    args = sys.argv[1:]
    if "--output" in args:
        idx = args.index("--output")
        if idx + 1 < len(args):
            output_path = args[idx + 1]

    device = await find_miband(timeout=8.0)
    await inspect_gatt(device.address, output_path)


if __name__ == "__main__":
    asyncio.run(main())

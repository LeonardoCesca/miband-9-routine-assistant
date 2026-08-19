from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from bleak import BleakScanner
from bleak.backends.device import BLEDevice
from bleak.backends.scanner import AdvertisementData

from app.config import get_settings
from app.miband.models import BandDiscoveryTimeout, BandUnavailableError

logger = logging.getLogger(__name__)


@dataclass
class FoundDevice:
    name: str
    address: str
    rssi: int


def _is_miband(name: str | None, address: str) -> bool:
    settings = get_settings()
    if settings.miband_ble_address and address.upper() == settings.miband_ble_address.upper():
        return True
    if settings.miband_ble_name and name and name == settings.miband_ble_name:
        return True
    return False


async def scan_devices(timeout: float = 10.0) -> list[FoundDevice]:
    logger.info("[BLE] Scanning for BLE devices...")
    devices: list[FoundDevice] = []

    def _callback(device: BLEDevice, adv: AdvertisementData) -> None:
        if device.name:
            devices.append(
                FoundDevice(
                    name=device.name,
                    address=device.address,
                    rssi=adv.rssi,
                )
            )

    scanner = BleakScanner(detection_callback=_callback)
    await scanner.start()
    await asyncio.sleep(timeout)
    await scanner.stop()

    logger.info("[BLE] Scan complete. Found %d devices.", len(devices))
    return devices


async def find_miband(timeout: float = 10.0) -> FoundDevice:
    settings = get_settings()

    if settings.miband_ble_address:
        logger.info("[BLE] Looking for Mi Band by address: %s", settings.miband_ble_address)
        devices = await scan_devices(timeout)
        for dev in devices:
            if dev.address.upper() == settings.miband_ble_address.upper():
                logger.info("[BLE] Mi Band found by address: %s", dev.address)
                return dev
        raise BandUnavailableError(
            "Mi Band 9 Pro not found by address. "
            "Verify the address and that the device is nearby."
        )

    if settings.miband_ble_name:
        logger.info("[BLE] Looking for Mi Band by name: %s", settings.miband_ble_name)
        devices = await scan_devices(timeout)
        for dev in devices:
            if dev.name == settings.miband_ble_name:
                logger.info("[BLE] Mi Band found: %s (%s)", dev.name, dev.address)
                return dev
        raise BandUnavailableError(
            f"Mi Band 9 Pro not found by name '{settings.miband_ble_name}'. "
            "Verify the device is nearby and Bluetooth is available."
        )

    logger.info("[BLE] No address or name configured. Listing all devices...")
    devices = await scan_devices(timeout)
    if not devices:
        raise BandDiscoveryTimeout("No BLE devices found.")
    return devices[0]

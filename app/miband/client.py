from __future__ import annotations

import logging

from bleak import BleakClient

from app.miband.models import BandConnectionError, BandState

logger = logging.getLogger(__name__)


class MiBandClient:
    def __init__(self, address: str) -> None:
        self._address = address
        self._client: BleakClient | None = None
        self._state = BandState.DISCONNECTED

    @property
    def state(self) -> BandState:
        return self._state

    @property
    def is_connected(self) -> bool:
        return self._client is not None and self._client.is_connected

    async def connect(self, timeout: float = 10.0) -> None:
        logger.info("[BLE] Connecting to %s", self._address)
        self._state = BandState.CONNECTING
        try:
            self._client = BleakClient(self._address, timeout=timeout)
            await self._client.connect()
            self._state = BandState.CONNECTED
            logger.info("[BLE] Connected")
        except Exception as exc:
            self._state = BandState.ERROR
            raise BandConnectionError(f"Failed to connect: {exc}") from exc

    async def disconnect(self) -> None:
        if self._client and self._client.is_connected:
            logger.info("[BLE] Disconnecting")
            await self._client.disconnect()
        self._client = None
        self._state = BandState.DISCONNECTED
        logger.info("[BLE] Disconnected")

    async def write(self, characteristic_uuid: str, data: bytes) -> None:
        if not self.is_connected:
            raise BandConnectionError("Not connected")
        assert self._client is not None
        await self._client.write_gatt_char(characteristic_uuid, data)

    async def read(self, characteristic_uuid: str) -> bytes:
        if not self.is_connected:
            raise BandConnectionError("Not connected")
        assert self._client is not None
        return await self._client.read_gatt_char(characteristic_uuid)

    async def start_notify(
        self, characteristic_uuid: str, callback
    ) -> None:
        if not self.is_connected:
            raise BandConnectionError("Not connected")
        assert self._client is not None
        await self._client.start_notify(characteristic_uuid, callback)

    async def stop_notify(self, characteristic_uuid: str) -> None:
        if not self.is_connected or self._client is None:
            return
        await self._client.stop_notify(characteristic_uuid)

    @property
    def services(self):
        if self._client is None:
            return []
        return self._client.services

    def set_state(self, state: BandState) -> None:
        self._state = state

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class TimeTool:
    def __init__(self, timezone_name: str) -> None:
        self._timezone = ZoneInfo(timezone_name)

    def now(self) -> datetime:
        return datetime.now(self._timezone)

    def matches_minute(self, *, hour: int, minute: int, current: datetime | None = None) -> bool:
        reference = current or self.now()
        return reference.hour == hour and reference.minute == minute

    def build_minute_key(self, reminder_id: str, current: datetime | None = None) -> str:
        reference = current or self.now()
        minute_stamp = reference.strftime("%Y%m%d%H%M")
        return f"{reminder_id}:{minute_stamp}"

    def plus_minutes(self, minutes: int, current: datetime | None = None) -> datetime:
        reference = current or self.now()
        return reference + timedelta(minutes=minutes)


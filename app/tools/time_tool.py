from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


class TimeTool:
    def __init__(self, timezone_name: str) -> None:
        self._timezone = ZoneInfo(timezone_name)

    def now(self) -> datetime:
        return datetime.now(self._timezone)

    def weekday(self, current: datetime | None = None) -> int:
        reference = current or self.now()
        return reference.weekday()

    def matches_weekday(
        self, days_of_week: list[int] | None, current: datetime | None = None
    ) -> bool:
        if not days_of_week:
            return True
        return self.weekday(current=current) in days_of_week

    def matches_minute(self, *, hour: int, minute: int, current: datetime | None = None) -> bool:
        reference = current or self.now()
        return reference.hour == hour and reference.minute == minute

    def floor_to_window(self, window_minutes: int, current: datetime | None = None) -> datetime:
        reference = current or self.now()
        floored_minute = reference.minute - (reference.minute % window_minutes)
        return reference.replace(minute=floored_minute, second=0, microsecond=0)

    def window_bounds(
        self, window_minutes: int, current: datetime | None = None
    ) -> tuple[datetime, datetime]:
        reference = current or self.now()
        return self.floor_to_window(window_minutes, current=reference), reference

    def matches_window(
        self,
        *,
        hour: int,
        minute: int,
        window_minutes: int,
        current: datetime | None = None,
    ) -> bool:
        reference = current or self.now()
        window_start = self.floor_to_window(window_minutes, current=reference)
        reminder_total = hour * 60 + minute
        start_total = window_start.hour * 60 + window_start.minute
        current_total = reference.hour * 60 + reference.minute
        return start_total <= reminder_total <= current_total

    def build_minute_key(self, reminder_id: str, current: datetime | None = None) -> str:
        reference = current or self.now()
        minute_stamp = reference.strftime("%Y%m%d%H%M")
        return f"{reminder_id}:{minute_stamp}"

    def build_window_key(
        self, reminder_id: str, window_minutes: int, current: datetime | None = None
    ) -> str:
        reference = self.floor_to_window(window_minutes, current=current)
        return f"{reminder_id}:{reference.strftime('%Y%m%d%H%M')}"

    def plus_minutes(self, minutes: int, current: datetime | None = None) -> datetime:
        reference = current or self.now()
        return reference + timedelta(minutes=minutes)

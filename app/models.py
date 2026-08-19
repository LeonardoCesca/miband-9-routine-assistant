from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HealthResponse(BaseModel):
    status: str = "ok"


class UserCreate(BaseModel):
    name: str = Field(min_length=1)
    telegram_chat_id: str = Field(min_length=1)


class UserRead(UserCreate):
    id: UUID
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ReminderCreate(BaseModel):
    user_id: UUID
    title: str = Field(min_length=1)
    message: str = Field(min_length=1)
    hour: int = Field(ge=0, le=23)
    minute: int = Field(default=0, ge=0, le=59)
    days_of_week: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])
    active: bool = True

    @field_validator("days_of_week")
    @classmethod
    def validate_days_of_week(cls, value: list[int]) -> list[int]:
        if not value:
            raise ValueError("days_of_week must contain at least one weekday")
        normalized = sorted(set(value))
        if any(day < 0 or day > 6 for day in normalized):
            raise ValueError("days_of_week values must be between 0 and 6")
        return normalized


class ReminderRead(ReminderCreate):
    id: UUID
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class ReminderToggleResponse(BaseModel):
    id: UUID
    active: bool


class ReminderLogRead(BaseModel):
    id: UUID | None = None
    user_id: UUID
    reminder_id: UUID
    status: Literal["sent", "done", "not_done", "postponed", "error"]
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime | None = None


class AnalyticsResponse(BaseModel):
    total: int
    done: int
    not_done: int
    postponed: int
    completion_rate: float


class InlineKeyboardButton(BaseModel):
    text: str
    callback_data: str


class InlineKeyboardMarkup(BaseModel):
    inline_keyboard: list[list[InlineKeyboardButton]]


class TelegramSendMessagePayload(BaseModel):
    chat_id: str
    text: str
    reply_markup: InlineKeyboardMarkup


class TelegramCallbackQuery(BaseModel):
    id: str
    data: str
    message: dict[str, Any]


class TelegramWebhookPayload(BaseModel):
    callback_query: TelegramCallbackQuery | None = None


class CallbackActionResult(BaseModel):
    status: Literal["done", "not_done", "postponed"]
    reminder_id: UUID
    user_id: UUID
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReminderDispatch(BaseModel):
    reminder_id: UUID
    user_id: UUID
    chat_id: str
    title: str
    message: str
    text: str
    reply_markup: InlineKeyboardMarkup
    dedupe_key: str


class SchedulerRunResponse(BaseModel):
    processed: int
    sent_keys: list[str]
    current_time: datetime
    window_minutes: int


class DashboardSummary(BaseModel):
    total_answered: int = 0
    done: int = 0
    not_done: int = 0
    postponed: int = 0
    completion_rate: float = 0


class DashboardActivityMetric(BaseModel):
    title: str
    sent: int = 0
    done: int = 0
    not_done: int = 0
    postponed: int = 0
    error: int = 0
    completion_rate: float = 0


class DashboardRecentLog(BaseModel):
    title: str
    status: str
    created_at: str
    message: str = ""


class DashboardMetricsResponse(BaseModel):
    summary: DashboardSummary
    activities: list[DashboardActivityMetric] = Field(default_factory=list)
    recent_logs: list[DashboardRecentLog] = Field(default_factory=list)

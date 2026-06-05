from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


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
    active: bool = True


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

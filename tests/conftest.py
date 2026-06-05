from __future__ import annotations

from collections.abc import Generator
from copy import deepcopy
from datetime import datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.logging_agent import LoggingAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.reminder_agent import ReminderAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.main import AppContainer, app
from app.tools.message_tool import MessageTool
from app.tools.time_tool import TimeTool


class FakeSupabaseTool:
    def __init__(self) -> None:
        self.users: list[dict] = []
        self.reminders: list[dict] = []
        self.logs: list[dict] = []

    def create_user(self, payload: dict) -> dict:
        created = {
            "id": str(uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            **payload,
        }
        self.users.append(created)
        return created

    def list_users(self) -> list[dict]:
        return deepcopy(self.users)

    def create_reminder(self, payload: dict) -> dict:
        created = {
            "id": str(uuid4()),
            "created_at": datetime.utcnow().isoformat(),
            **payload,
        }
        self.reminders.append(created)
        return created

    def list_reminders(self) -> list[dict]:
        return deepcopy(self.reminders)

    def list_active_reminders(self) -> list[dict]:
        return [deepcopy(item) for item in self.reminders if item["active"]]

    def get_reminder(self, reminder_id: str) -> dict | None:
        for reminder in self.reminders:
            if reminder["id"] == reminder_id:
                return deepcopy(reminder)
        return None

    def toggle_reminder(self, reminder_id: str) -> dict:
        for reminder in self.reminders:
            if reminder["id"] == reminder_id:
                reminder["active"] = not reminder["active"]
                return deepcopy(reminder)
        raise ValueError("Reminder not found")

    def save_log(self, *, user_id: str, reminder_id: str, status: str, metadata: dict | None = None) -> dict:
        created = {
            "id": str(uuid4()),
            "user_id": user_id,
            "reminder_id": reminder_id,
            "status": status,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        self.logs.append(created)
        return created

    def list_logs(self) -> list[dict]:
        return deepcopy(self.logs)


class FakeTelegramTool:
    def __init__(self) -> None:
        self.sent_messages: list[dict] = []
        self.answered_callbacks: list[dict] = []

    async def send_message(self, payload) -> dict:
        data = payload.model_dump(mode="json")
        self.sent_messages.append(data)
        return {"ok": True, "result": data}

    async def answer_callback_query(self, callback_query_id: str, text: str) -> dict:
        data = {"callback_query_id": callback_query_id, "text": text}
        self.answered_callbacks.append(data)
        return {"ok": True, "result": data}


class FixedTimeTool(TimeTool):
    def __init__(self) -> None:
        super().__init__("America/Sao_Paulo")
        self.current = datetime.fromisoformat("2026-06-05T09:30:00-03:00")

    def now(self) -> datetime:
        return self.current


@pytest.fixture
def container() -> AppContainer:
    supabase_tool = FakeSupabaseTool()
    telegram_tool = FakeTelegramTool()
    time_tool = FixedTimeTool()
    message_tool = MessageTool()

    logging_agent = LoggingAgent(supabase_tool)  # type: ignore[arg-type]
    reminder_agent = ReminderAgent(supabase_tool, message_tool, time_tool)  # type: ignore[arg-type]
    notification_agent = NotificationAgent(telegram_tool)  # type: ignore[arg-type]
    orchestrator_agent = OrchestratorAgent(reminder_agent, notification_agent, logging_agent)
    scheduler_agent = SchedulerAgent(orchestrator_agent, time_tool)
    analytics_agent = AnalyticsAgent(supabase_tool)  # type: ignore[arg-type]

    return AppContainer(
        supabase_tool=supabase_tool,  # type: ignore[arg-type]
        time_tool=time_tool,
        message_tool=message_tool,
        telegram_tool=telegram_tool,  # type: ignore[arg-type]
        logging_agent=logging_agent,
        reminder_agent=reminder_agent,
        notification_agent=notification_agent,
        orchestrator_agent=orchestrator_agent,
        scheduler_agent=scheduler_agent,
        analytics_agent=analytics_agent,
    )


@pytest.fixture
def client(container: AppContainer) -> Generator[TestClient, None, None]:
    original_container = app.state.container
    app.state.container = container
    with TestClient(app) as test_client:
        yield test_client
    app.state.container = original_container


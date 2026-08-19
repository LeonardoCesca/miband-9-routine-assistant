from __future__ import annotations

from collections.abc import Generator
from copy import deepcopy
from datetime import UTC, datetime
import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.logging_agent import LoggingAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.reminder_agent import ReminderAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.config import get_settings
from app.main import AppContainer, app
from app.notifications.service import NotificationService
from app.notifications.transport import NotificationTransport
from app.tools.message_tool import MessageTool
from app.tools.time_tool import TimeTool


class FakeSupabaseTool:
    def __init__(self) -> None:
        self.users: list[dict] = []
        self.reminders: list[dict] = []
        self.logs: list[dict] = []
        self.now_provider = lambda: datetime.now(UTC)

    def create_user(self, payload: dict) -> dict:
        created = {
            "id": str(uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
            **payload,
        }
        self.users.append(created)
        return created

    def list_users(self) -> list[dict]:
        return deepcopy(self.users)

    def create_reminder(self, payload: dict) -> dict:
        created = {
            "id": str(uuid4()),
            "created_at": datetime.now(UTC).isoformat(),
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
            "created_at": self.now_provider().isoformat(),
        }
        self.logs.append(created)
        return created

    def list_logs(self) -> list[dict]:
        return deepcopy(self.logs)

    def has_sent_log_in_window(self, *, reminder_id: str, window_start, window_end) -> bool:
        for log in self.logs:
            if log["reminder_id"] != reminder_id or log["status"] != "sent":
                continue
            created_at = datetime.fromisoformat(log["created_at"])
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=window_end.tzinfo)
            if window_start <= created_at <= window_end:
                return True
        return False


class FakeNotificationTransport(NotificationTransport):
    def __init__(self) -> None:
        self.sent: list[dict[str, str]] = []

    async def connect(self) -> None:
        pass

    async def disconnect(self) -> None:
        pass

    async def send(self, title: str, message: str) -> None:
        self.sent.append({"title": title, "message": message})


class FixedTimeTool(TimeTool):
    def __init__(self) -> None:
        super().__init__("America/Sao_Paulo")
        self.current = datetime.fromisoformat("2026-06-05T09:30:00-03:00")

    def now(self) -> datetime:
        return self.current


@pytest.fixture
def container() -> AppContainer:
    supabase_tool = FakeSupabaseTool()
    time_tool = FixedTimeTool()
    message_tool = MessageTool()
    supabase_tool.now_provider = time_tool.now

    transport = FakeNotificationTransport()
    notification_service = NotificationService(transport)

    logging_agent = LoggingAgent(supabase_tool)  # type: ignore[arg-type]
    reminder_agent = ReminderAgent(supabase_tool, message_tool, time_tool)  # type: ignore[arg-type]
    notification_agent = NotificationAgent(notification_service)
    orchestrator_agent = OrchestratorAgent(reminder_agent, notification_agent, logging_agent)
    scheduler_agent = SchedulerAgent(orchestrator_agent, window_minutes=5)
    analytics_agent = AnalyticsAgent(supabase_tool, time_tool)  # type: ignore[arg-type]

    return AppContainer(
        supabase_tool=supabase_tool,  # type: ignore[arg-type]
        time_tool=time_tool,
        message_tool=message_tool,
        notification_service=notification_service,
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
    original_scheduler_token = os.environ.get("SCHEDULER_TOKEN")
    os.environ["SCHEDULER_TOKEN"] = "test-scheduler-token"
    get_settings.cache_clear()
    app.state.container = container
    with TestClient(app) as test_client:
        yield test_client
    app.state.container = original_container
    get_settings.cache_clear()
    if original_scheduler_token is None:
        os.environ.pop("SCHEDULER_TOKEN", None)
    else:
        os.environ["SCHEDULER_TOKEN"] = original_scheduler_token

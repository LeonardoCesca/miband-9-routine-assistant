from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import FastAPI, HTTPException, status

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.logging_agent import LoggingAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.reminder_agent import ReminderAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.config import get_settings
from app.database import get_supabase_client
from app.models import CallbackActionResult, HealthResponse
from app.routes import analytics, reminders, telegram, users
from app.services.supabase_service import SupabaseService
from app.services.telegram_service import TelegramService
from app.tools.message_tool import MessageTool
from app.tools.supabase_tool import SupabaseTool
from app.tools.telegram_tool import TelegramTool
from app.tools.time_tool import TimeTool


@dataclass
class AppContainer:
    supabase_tool: SupabaseTool
    time_tool: TimeTool
    message_tool: MessageTool
    telegram_tool: TelegramTool
    logging_agent: LoggingAgent
    reminder_agent: ReminderAgent
    notification_agent: NotificationAgent
    orchestrator_agent: OrchestratorAgent
    scheduler_agent: SchedulerAgent
    analytics_agent: AnalyticsAgent

    async def handle_callback(
        self, callback_data: str, callback_query_id: str | None = None
    ) -> CallbackActionResult:
        action, reminder_id = self._parse_callback_data(callback_data)
        reminder = self.supabase_tool.get_reminder(reminder_id)
        if reminder is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

        current = self.time_tool.now()
        metadata: dict[str, Any] = {}
        if action == "postponed":
            metadata = {
                "current_time": current.isoformat(),
                "suggested_time": self.time_tool.plus_minutes(15, current=current).isoformat(),
            }

        self.logging_agent.log(
            user_id=str(reminder["user_id"]),
            reminder_id=reminder_id,
            status=action,
            metadata=metadata,
        )
        return CallbackActionResult(
            status=action,
            reminder_id=reminder["id"],
            user_id=reminder["user_id"],
            metadata=metadata,
        )

    @staticmethod
    def _parse_callback_data(callback_data: str) -> tuple[str, str]:
        parts = callback_data.split(":", maxsplit=1)
        if len(parts) != 2 or parts[0] not in {"done", "not_done", "postponed"}:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid callback")
        return parts[0], parts[1]


def build_container() -> AppContainer:
    settings = get_settings()
    supabase_service = SupabaseService(get_supabase_client())
    telegram_service = TelegramService(settings.telegram_bot_token)

    supabase_tool = SupabaseTool(supabase_service)
    time_tool = TimeTool(settings.app_timezone)
    message_tool = MessageTool()
    telegram_tool = TelegramTool(telegram_service)

    logging_agent = LoggingAgent(supabase_tool)
    reminder_agent = ReminderAgent(supabase_tool, message_tool, time_tool)
    notification_agent = NotificationAgent(telegram_tool)
    orchestrator_agent = OrchestratorAgent(reminder_agent, notification_agent, logging_agent)
    scheduler_agent = SchedulerAgent(orchestrator_agent, time_tool)
    analytics_agent = AnalyticsAgent(supabase_tool)

    return AppContainer(
        supabase_tool=supabase_tool,
        time_tool=time_tool,
        message_tool=message_tool,
        telegram_tool=telegram_tool,
        logging_agent=logging_agent,
        reminder_agent=reminder_agent,
        notification_agent=notification_agent,
        orchestrator_agent=orchestrator_agent,
        scheduler_agent=scheduler_agent,
        analytics_agent=analytics_agent,
    )


app = FastAPI(title="band-routine-assistant", version="0.1.0")
app.state.container = None


@app.on_event("startup")
async def on_startup() -> None:
    if app.state.container is None:
        app.state.container = build_container()
    app.state.container.scheduler_agent.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    app.state.container.scheduler_agent.shutdown()


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse()


app.include_router(users.router)
app.include_router(reminders.router)
app.include_router(telegram.router)
app.include_router(analytics.router)

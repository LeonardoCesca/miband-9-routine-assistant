from __future__ import annotations

from dataclasses import dataclass

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.logging_agent import LoggingAgent
from app.agents.notification_agent import NotificationAgent
from app.agents.orchestrator_agent import OrchestratorAgent
from app.agents.reminder_agent import ReminderAgent
from app.agents.scheduler_agent import SchedulerAgent
from app.config import get_settings
from app.database import get_supabase_client
from app.models import HealthResponse
from app.notifications.factory import create_transport
from app.notifications.service import NotificationService
from app.routes import analytics, dashboard, reminders, scheduler, users
from app.services.supabase_service import SupabaseService
from app.tools.message_tool import MessageTool
from app.tools.supabase_tool import SupabaseTool
from app.tools.time_tool import TimeTool


@dataclass
class AppContainer:
    supabase_tool: SupabaseTool
    time_tool: TimeTool
    message_tool: MessageTool
    notification_service: NotificationService
    logging_agent: LoggingAgent
    reminder_agent: ReminderAgent
    notification_agent: NotificationAgent
    orchestrator_agent: OrchestratorAgent
    scheduler_agent: SchedulerAgent
    analytics_agent: AnalyticsAgent


def build_container() -> AppContainer:
    settings = get_settings()
    supabase_service = SupabaseService(get_supabase_client())

    supabase_tool = SupabaseTool(supabase_service)
    time_tool = TimeTool(settings.app_timezone)
    message_tool = MessageTool()

    transport = create_transport(settings)
    notification_service = NotificationService(transport)

    logging_agent = LoggingAgent(supabase_tool)
    reminder_agent = ReminderAgent(supabase_tool, message_tool, time_tool)
    notification_agent = NotificationAgent(notification_service)
    orchestrator_agent = OrchestratorAgent(reminder_agent, notification_agent, logging_agent)
    scheduler_agent = SchedulerAgent(orchestrator_agent, window_minutes=5)
    analytics_agent = AnalyticsAgent(supabase_tool, time_tool)

    return AppContainer(
        supabase_tool=supabase_tool,
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


app = FastAPI(title="band-routine-assistant", version="0.1.0")
app.state.container = None
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
async def on_startup() -> None:
    if app.state.container is None:
        app.state.container = build_container()


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    return HealthResponse()


app.include_router(users.router)
app.include_router(reminders.router)
app.include_router(analytics.router)
app.include_router(scheduler.router)
app.include_router(dashboard.router)

from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.agents.orchestrator_agent import OrchestratorAgent
from app.tools.time_tool import TimeTool


class SchedulerAgent:
    def __init__(self, orchestrator_agent: OrchestratorAgent, time_tool: TimeTool) -> None:
        self._orchestrator_agent = orchestrator_agent
        self._time_tool = time_tool
        self._processed_keys: set[str] = set()
        self._scheduler = AsyncIOScheduler(timezone=time_tool.now().tzinfo)

    @property
    def processed_keys(self) -> set[str]:
        return self._processed_keys

    async def tick(self) -> list[str]:
        self._cleanup_processed_keys()
        return await self._orchestrator_agent.run_due_reminders(self._processed_keys)

    def start(self) -> None:
        if not self._scheduler.get_jobs():
            self._scheduler.add_job(
                self.tick,
                IntervalTrigger(minutes=1, timezone=self._time_tool.now().tzinfo),
                id="reminder-tick",
                replace_existing=True,
            )
        if not self._scheduler.running:
            self._scheduler.start()

    def shutdown(self) -> None:
        if self._scheduler.running:
            self._scheduler.shutdown(wait=False)

    def _cleanup_processed_keys(self) -> None:
        current_prefix = self._time_tool.now().strftime("%Y%m%d%H%M")
        self._processed_keys = {
            key for key in self._processed_keys if key.split(":")[-1] >= current_prefix
        }

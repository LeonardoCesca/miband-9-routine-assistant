from __future__ import annotations

from app.agents.orchestrator_agent import OrchestratorAgent


class SchedulerAgent:
    def __init__(self, orchestrator_agent: OrchestratorAgent, window_minutes: int = 5) -> None:
        self._orchestrator_agent = orchestrator_agent
        self._window_minutes = window_minutes

    async def tick(self) -> list[str]:
        return await self._orchestrator_agent.run_due_reminders(
            window_minutes=self._window_minutes
        )

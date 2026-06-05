from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.config import get_settings
from app.dependencies import get_container
from app.models import SchedulerRunResponse

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


@router.post("/run", response_model=SchedulerRunResponse)
async def run_scheduler(
    container=Depends(get_container),
    x_scheduler_token: str | None = Header(default=None, alias="X-Scheduler-Token"),
) -> SchedulerRunResponse:
    settings = get_settings()
    if not settings.scheduler_token or x_scheduler_token != settings.scheduler_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid scheduler token",
        )

    sent_keys = await container.scheduler_agent.tick()
    return SchedulerRunResponse(processed=len(sent_keys), sent_keys=sent_keys)

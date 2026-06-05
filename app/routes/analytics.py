from fastapi import APIRouter, Depends

from app.dependencies import get_container
from app.models import AnalyticsResponse

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
def get_analytics(container=Depends(get_container)) -> AnalyticsResponse:
    return container.analytics_agent.summarize()

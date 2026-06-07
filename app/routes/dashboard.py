from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import get_container
from app.models import DashboardMetricsResponse

router = APIRouter(tags=["dashboard"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, container=Depends(get_container)) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "page_title": "Band Routine Dashboard",
            "subtitle": "Monitoramento de habitos, treinos e consistencia",
        },
    )


@router.get("/api/dashboard/metrics", response_model=DashboardMetricsResponse)
def dashboard_metrics(container=Depends(get_container)) -> DashboardMetricsResponse:
    return container.analytics_agent.get_dashboard_metrics()

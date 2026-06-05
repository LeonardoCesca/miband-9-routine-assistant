from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_container
from app.models import ReminderCreate, ReminderRead, ReminderToggleResponse
from app.tools.supabase_tool import SupabaseToolError

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.post("", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(
    payload: ReminderCreate, container=Depends(get_container)
) -> ReminderRead:
    created = container.supabase_tool.create_reminder(payload.model_dump(mode="json"))
    return ReminderRead.model_validate(created)


@router.get("", response_model=list[ReminderRead])
def list_reminders(container=Depends(get_container)) -> list[ReminderRead]:
    return [
        ReminderRead.model_validate(item) for item in container.supabase_tool.list_reminders()
    ]


@router.patch("/{reminder_id}/toggle", response_model=ReminderToggleResponse)
def toggle_reminder(
    reminder_id: UUID, container=Depends(get_container)
) -> ReminderToggleResponse:
    try:
        updated = container.supabase_tool.toggle_reminder(str(reminder_id))
    except SupabaseToolError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ReminderToggleResponse.model_validate(updated)

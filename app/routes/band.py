from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_container

router = APIRouter(prefix="/band", tags=["band"])


@router.post("/callback", status_code=status.HTTP_200_OK)
async def band_callback(
    reminder_id: str = Query(...),
    action: str = Query(...),
    container=Depends(get_container),
) -> dict[str, str]:
    if action not in {"done", "not_done", "postponed"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be done, not_done, or postponed.",
        )

    try:
        UUID(reminder_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reminder_id format.",
        )

    result = await container.handle_callback(f"{action}:{reminder_id}")
    return {"status": result.status, "reminder_id": str(result.reminder_id)}

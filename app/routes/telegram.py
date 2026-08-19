from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.dependencies import get_container
from app.models import TelegramWebhookPayload

router = APIRouter(prefix="/telegram", tags=["telegram"])


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def telegram_webhook(
    payload: TelegramWebhookPayload,
    container=Depends(get_container),
) -> dict[str, str]:
    callback_query = payload.callback_query
    if callback_query is None:
        return {"status": "ignored"}

    result = await container.handle_callback(callback_query.data, callback_query.id)
    await container.notification_agent.answer_callback(
        callback_query.id,
        f"Ação registrada: {result.status}",
    )
    return {"status": result.status}

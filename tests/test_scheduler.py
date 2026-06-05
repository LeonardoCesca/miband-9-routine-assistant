import pytest


def test_scheduler_route_requires_token(client):
    response = client.post("/scheduler/run")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid scheduler token"


@pytest.mark.asyncio
async def test_scheduler_route_processes_pending_window(client, container):
    user = container.supabase_tool.create_user(
        {"name": "Leona", "telegram_chat_id": "123456"}
    )
    container.supabase_tool.create_reminder(
        {
            "user_id": user["id"],
            "title": "Alongar",
            "message": "Hora da rotina",
            "hour": 9,
            "minute": 30,
            "active": True,
        }
    )

    response = client.post(
        "/scheduler/run",
        headers={"X-Scheduler-Token": "test-scheduler-token"},
    )

    assert response.status_code == 200
    assert response.json()["processed"] == 1
    assert len(container.telegram_tool.sent_messages) == 1

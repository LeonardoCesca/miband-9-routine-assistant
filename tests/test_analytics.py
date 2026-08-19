from pathlib import Path

import pytest


def test_analytics_completion_rate(client, container):
    user = client.post("/users", json={"name": "Leona", "telegram_chat_id": "123456"}).json()
    reminder = client.post(
        "/reminders",
        json={
            "user_id": user["id"],
            "title": "Alongar",
            "message": "Hora da rotina",
            "hour": 9,
            "minute": 30,
            "days_of_week": [4],
            "active": True,
        },
    ).json()

    container.supabase_tool.save_log(
        user_id=user["id"], reminder_id=reminder["id"], status="done", metadata={}
    )
    container.supabase_tool.save_log(
        user_id=user["id"], reminder_id=reminder["id"], status="postponed", metadata={}
    )
    container.supabase_tool.save_log(
        user_id=user["id"], reminder_id=reminder["id"], status="not_done", metadata={}
    )

    response = client.get("/analytics")

    assert response.status_code == 200
    assert response.json()["completion_rate"] == 33.33


@pytest.mark.asyncio
async def test_scheduler_agent_does_not_duplicate_same_window(container):
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
            "days_of_week": [4],
            "active": True,
        }
    )

    first_run = await container.scheduler_agent.tick()
    second_run = await container.scheduler_agent.tick()

    assert len(first_run) == 1
    assert second_run == []
    assert len(container.telegram_tool.sent_messages) == 1


@pytest.mark.asyncio
async def test_scheduler_agent_respects_weekday(container):
    user = container.supabase_tool.create_user(
        {"name": "Leona", "telegram_chat_id": "123456"}
    )
    container.supabase_tool.create_reminder(
        {
            "user_id": user["id"],
            "title": "Dia errado",
            "message": "Nao deve enviar hoje",
            "hour": 9,
            "minute": 30,
            "days_of_week": [0],
            "active": True,
        }
    )

    result = await container.scheduler_agent.tick()

    assert result == []
    assert len(container.telegram_tool.sent_messages) == 0


def test_no_tokens_are_hardcoded():
    repo_root = Path(__file__).resolve().parents[1]
    for path in repo_root.rglob("*"):
        if path.is_dir() or path.name in {".env", "test_analytics.py"}:
            continue
        if path.suffix in {".pyc"}:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        assert "123456:ABCDEF" not in content
        assert "TELEGRAM_BOT_TOKEN=real_token" not in content
        assert "SUPABASE_SERVICE_ROLE_KEY=real_key" not in content


def test_dotenv_is_in_gitignore():
    repo_root = Path(__file__).resolve().parents[1]
    content = (repo_root / ".gitignore").read_text(encoding="utf-8")

    assert ".env" in content


def test_dotenv_example_exists():
    repo_root = Path(__file__).resolve().parents[1]

    assert (repo_root / ".env.example").exists()

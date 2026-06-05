def _create_user_and_reminder(client):
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
    return user, reminder


def test_done_callback_saves_done_status(client, container):
    _, reminder = _create_user_and_reminder(client)

    response = client.post(
        "/telegram/webhook",
        json={
            "callback_query": {
                "id": "cbq-1",
                "data": f"done:{reminder['id']}",
                "message": {"message_id": 1},
            }
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "done"}
    assert container.supabase_tool.logs[-1]["status"] == "done"


def test_not_done_callback_saves_not_done_status(client, container):
    _, reminder = _create_user_and_reminder(client)

    response = client.post(
        "/telegram/webhook",
        json={
            "callback_query": {
                "id": "cbq-2",
                "data": f"not_done:{reminder['id']}",
                "message": {"message_id": 1},
            }
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "not_done"}
    assert container.supabase_tool.logs[-1]["status"] == "not_done"


def test_postponed_callback_saves_postponed_status(client, container):
    _, reminder = _create_user_and_reminder(client)

    response = client.post(
        "/telegram/webhook",
        json={
            "callback_query": {
                "id": "cbq-3",
                "data": f"postponed:{reminder['id']}",
                "message": {"message_id": 1},
            }
        },
    )

    assert response.status_code == 200
    assert response.json() == {"status": "postponed"}
    log = container.supabase_tool.logs[-1]
    assert log["status"] == "postponed"
    assert "current_time" in log["metadata"]
    assert "suggested_time" in log["metadata"]
    assert container.telegram_tool.answered_callbacks[-1]["callback_query_id"] == "cbq-3"

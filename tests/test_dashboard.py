def test_dashboard_page_returns_200(client):
    response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Band Routine Dashboard" in response.text


def test_dashboard_metrics_returns_valid_json(client, container):
    user = container.supabase_tool.create_user({"name": "Leona", "telegram_chat_id": "123456"})
    reminder = container.supabase_tool.create_reminder(
        {
            "user_id": user["id"],
            "title": "Segunda - Peitoral",
            "message": "Hora da rotina",
            "hour": 9,
            "minute": 30,
            "days_of_week": [4],
            "active": True,
        }
    )
    container.supabase_tool.save_log(
        user_id=user["id"], reminder_id=reminder["id"], status="done", metadata={}
    )

    response = client.get("/api/dashboard/metrics")

    assert response.status_code == 200
    body = response.json()
    assert "summary" in body
    assert "activities" in body
    assert "recent_logs" in body


def test_dashboard_completion_rate_zero_when_no_answered_logs(client):
    response = client.get("/api/dashboard/metrics")

    assert response.status_code == 200
    assert response.json()["summary"]["completion_rate"] == 0


def test_dashboard_sent_status_not_counted_in_completion(client, container):
    user = container.supabase_tool.create_user({"name": "Leona", "telegram_chat_id": "123456"})
    reminder = container.supabase_tool.create_reminder(
        {
            "user_id": user["id"],
            "title": "Segunda - Peitoral",
            "message": "Hora da rotina",
            "hour": 9,
            "minute": 30,
            "days_of_week": [4],
            "active": True,
        }
    )
    container.supabase_tool.save_log(
        user_id=user["id"], reminder_id=reminder["id"], status="sent", metadata={}
    )

    response = client.get("/api/dashboard/metrics")

    assert response.status_code == 200
    summary = response.json()["summary"]
    assert summary["total_answered"] == 0
    assert summary["completion_rate"] == 0


def test_dashboard_activity_metrics_are_calculated_correctly(client, container):
    user = container.supabase_tool.create_user({"name": "Leona", "telegram_chat_id": "123456"})
    reminder = container.supabase_tool.create_reminder(
        {
            "user_id": user["id"],
            "title": "Segunda - Peitoral",
            "message": "Hora da rotina",
            "hour": 9,
            "minute": 30,
            "days_of_week": [4],
            "active": True,
        }
    )
    container.supabase_tool.save_log(
        user_id=user["id"], reminder_id=reminder["id"], status="done", metadata={}
    )
    container.supabase_tool.save_log(
        user_id=user["id"], reminder_id=reminder["id"], status="not_done", metadata={}
    )
    container.supabase_tool.save_log(
        user_id=user["id"], reminder_id=reminder["id"], status="postponed", metadata={}
    )

    response = client.get("/api/dashboard/metrics")

    activity = next(item for item in response.json()["activities"] if item["title"] == "Peitoral")
    assert activity["done"] == 1
    assert activity["not_done"] == 1
    assert activity["postponed"] == 1
    assert activity["completion_rate"] == 33.33

def test_create_reminder(client):
    user = client.post("/users", json={"name": "Leona", "telegram_chat_id": "123456"}).json()

    response = client.post(
        "/reminders",
        json={
            "user_id": user["id"],
            "title": "Alongar",
            "message": "Hora da rotina",
            "hour": 9,
            "minute": 30,
            "active": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Alongar"
    assert body["minute"] == 30


def test_list_reminders(client):
    user = client.post("/users", json={"name": "Leona", "telegram_chat_id": "123456"}).json()
    client.post(
        "/reminders",
        json={
            "user_id": user["id"],
            "title": "Alongar",
            "message": "Hora da rotina",
            "hour": 9,
            "minute": 30,
            "active": True,
        },
    )

    response = client.get("/reminders")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_toggle_reminder(client):
    user = client.post("/users", json={"name": "Leona", "telegram_chat_id": "123456"}).json()
    reminder = client.post(
        "/reminders",
        json={
            "user_id": user["id"],
            "title": "Alongar",
            "message": "Hora da rotina",
            "hour": 9,
            "minute": 30,
            "active": True,
        },
    ).json()

    response = client.patch(f"/reminders/{reminder['id']}/toggle")

    assert response.status_code == 200
    assert response.json()["active"] is False


def test_message_tool_builds_buttons(container):
    reminder_id = "abc-123"

    keyboard = container.message_tool.build_keyboard(reminder_id)

    assert keyboard.inline_keyboard[0][0].callback_data == f"done:{reminder_id}"
    assert keyboard.inline_keyboard[0][1].callback_data == f"not_done:{reminder_id}"
    assert keyboard.inline_keyboard[1][0].callback_data == f"postponed:{reminder_id}"


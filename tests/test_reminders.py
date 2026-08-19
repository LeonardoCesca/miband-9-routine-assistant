def test_create_reminder(client):
    user = client.post("/users", json={"name": "Leona"}).json()

    response = client.post(
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
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Alongar"
    assert body["minute"] == 30
    assert body["days_of_week"] == [4]


def test_list_reminders(client):
    user = client.post("/users", json={"name": "Leona"}).json()
    client.post(
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
    )

    response = client.get("/reminders")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_toggle_reminder(client):
    user = client.post("/users", json={"name": "Leona"}).json()
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

    response = client.patch(f"/reminders/{reminder['id']}/toggle")

    assert response.status_code == 200
    assert response.json()["active"] is False


def test_message_tool_builds_text(container):
    text = container.message_tool.build_text(title="Alongar", message="Hora da rotina")

    assert text == "Alongar\nHora da rotina"

def test_create_user(client):
    response = client.post(
        "/users",
        json={"name": "Leona", "telegram_chat_id": "123456"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Leona"
    assert body["telegram_chat_id"] == "123456"
    assert "id" in body


def test_list_users(client):
    client.post("/users", json={"name": "Leona", "telegram_chat_id": "123456"})
    client.post("/users", json={"name": "Bia", "telegram_chat_id": "654321"})

    response = client.get("/users")

    assert response.status_code == 200
    assert len(response.json()) == 2


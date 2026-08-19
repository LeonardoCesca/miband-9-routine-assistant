def test_create_user(client):
    response = client.post(
        "/users",
        json={"name": "Leona"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Leona"
    assert "id" in body


def test_list_users(client):
    client.post("/users", json={"name": "Leona"})
    client.post("/users", json={"name": "Bia"})

    response = client.get("/users")

    assert response.status_code == 200
    assert len(response.json()) == 2

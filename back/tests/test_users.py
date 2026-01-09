def test_create_user_success(client):
    payload = {"username": "alice", "password": "secret123"}
    resp = client.post("/api/users", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["username"] == "alice"


def test_create_user_conflict(client):
    payload = {"username": "bob", "password": "secret123"}
    resp1 = client.post("/api/users", json=payload)
    assert resp1.status_code == 201

    resp2 = client.post("/api/users", json=payload)
    assert resp2.status_code == 409
    assert resp2.json()["detail"] == "Username already taken"


def test_create_user_validation(client):
    # Too short username and password
    payload = {"username": "ab", "password": "123"}
    resp = client.post("/api/users", json=payload)
    # Pydantic validation should fail with 422
    assert resp.status_code == 422

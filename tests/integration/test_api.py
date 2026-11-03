"""Integration tests for the HTTP API, backed by a real PostgreSQL database."""

import pytest

VALID = {"username": "alice", "email": "alice@example.com", "password": "SecurePass123"}


def test_register_user(client):
    response = client.post("/users/register", json=VALID)

    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "alice"
    assert body["email"] == "alice@example.com"
    assert "id" in body and "created_at" in body
    assert "password" not in body and "password_hash" not in body


def test_register_duplicate_username(client):
    client.post("/users/register", json=VALID)
    response = client.post("/users/register", json={**VALID, "email": "new@example.com"})
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_register_duplicate_email(client):
    client.post("/users/register", json=VALID)
    response = client.post("/users/register", json={**VALID, "username": "alice2"})
    assert response.status_code == 400


@pytest.mark.parametrize("field, value", [
    ("email", "not-an-email"),
    ("password", "short"),
    ("username", "a"),
])
def test_register_invalid_data_returns_422(client, field, value):
    response = client.post("/users/register", json={**VALID, field: value})
    assert response.status_code == 422


def test_read_user(client):
    user_id = client.post("/users/register", json=VALID).json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == "alice"
    assert "password_hash" not in response.json()


def test_read_missing_user(client):
    assert client.get("/users/9999").status_code == 404


@pytest.mark.parametrize("operation, a, b, expected", [
    ("add", 2, 3, 5),
    ("subtract", 5, 3, 2),
    ("multiply", 4, 5, 20),
    ("divide", 10, 2, 5),
])
def test_calculator_endpoints(client, operation, a, b, expected):
    response = client.post(f"/{operation}", json={"a": a, "b": b})
    assert response.status_code == 200
    assert response.json()["result"] == expected


def test_divide_by_zero_endpoint(client):
    response = client.post("/divide", json={"a": 1, "b": 0})
    assert response.status_code == 400
    assert "Cannot divide by zero" in response.json()["detail"]


def test_unknown_operation(client):
    assert client.post("/modulo", json={"a": 1, "b": 2}).status_code == 404


def test_index_and_health(client):
    assert client.get("/").status_code == 200
    assert "Calculator" in client.get("/").text
    assert client.get("/health").json() == {"status": "ok"}
#!/usr/bin/env python3
"""Authentication API flow tests using in-process TestClient."""

import pytest


@pytest.mark.usefixtures("client")
def test_auth_flow(client):
    # 1. Signup
    signup_payload = {
        "name": "Test User 2",
        "email": "test2@example.com",
        "password": "testpassword123",
    }
    signup_resp = client.post("/api/signup", json=signup_payload)
    # Either 201 (created) or 400 if already exists from prior run
    assert signup_resp.status_code in (201, 400)
    if signup_resp.status_code == 400:
        # Ensure correct error semantics
        body = signup_resp.json()
        assert "detail" in body

    # 2. Login
    login_resp = client.post(
        "/api/login", json={"email": signup_payload["email"], "password": signup_payload["password"]}
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert data["message"].lower().startswith("login")
    assert "user_id" in data

    # 3. Current user via /users (returns list with one user)
    users_resp = client.get("/api/users")
    assert users_resp.status_code == 200
    users = users_resp.json()
    assert isinstance(users, list) and len(users) == 1
    assert users[0]["email"] == signup_payload["email"]

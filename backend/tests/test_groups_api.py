#!/usr/bin/env python3
"""Tests to verify the API returns correct group data."""


def test_groups_api_response(client, unique_email):
    """Ensure group listing includes newly created groups for the signed-in user."""
    signup_payload = {
        "name": "Test User",
        "email": unique_email,
        "password": "testpass123",
    }
    signup_response = client.post("/api/signup", json=signup_payload)
    assert signup_response.status_code == 201
    user_id = signup_response.json()["user_id"]

    csrf_response = client.get("/api/csrf-token")
    assert csrf_response.status_code == 200
    csrf_token = csrf_response.json()["csrf_token"]

    group_payload = {"name": "Test Group", "member_ids": [], "member_emails": []}
    create_response = client.post(
        "/api/groups", json=group_payload, headers={"X-CSRF-Token": csrf_token}
    )
    assert create_response.status_code == 201

    groups_response = client.get("/api/groups")
    assert groups_response.status_code == 200
    groups = groups_response.json()
    assert any(group["name"] == "Test Group" for group in groups)

    created_group = next(group for group in groups if group["name"] == "Test Group")
    assert user_id in created_group.get("members", {})

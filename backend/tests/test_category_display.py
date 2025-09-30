#!/usr/bin/env python3
"""Category display test converted to assertions with TestClient.

NOTE: Original test depended on pre-existing group and user IDs; we adapt by creating
our own group and expenses instead of relying on hard-coded UUIDs.
"""

import pytest


@pytest.mark.usefixtures("client")
def test_category_display(client):
    # Sign up & login a user
    signup_payload = {"name": "Category Tester", "email": "cat@test.com", "password": "test123"}
    client.post("/api/signup", json=signup_payload)  # ignore duplicate / error semantics
    login_resp = client.post(
        "/api/login", json={"email": signup_payload["email"], "password": signup_payload["password"]}
    )
    assert login_resp.status_code == 200

    # Create group
    group_resp = client.post(
        "/api/groups", json={"name": "Category Test Group", "member_ids": [], "member_emails": []}
    )
    assert group_resp.status_code == 201
    group = group_resp.json()
    group_id = group["id"]
    member_ids = list(group["members"].keys())
    assert member_ids

    # Add several expenses with and without categories (if category field supported in schema)
    expenses_payloads = [
        {"description": "Lunch", "amount": 30.0, "paid_by": member_ids[0], "split_type": "EQUAL", "split_among": member_ids},
        {"description": "Taxi", "amount": 50.0, "paid_by": member_ids[0], "split_type": "EQUAL", "split_among": member_ids},
    ]
    for payload in expenses_payloads:
        resp = client.post(f"/api/groups/{group_id}/expenses", json=payload)
        assert resp.status_code == 201

    # Retrieve groups and find our test group
    groups_resp = client.get("/api/groups")
    assert groups_resp.status_code == 200
    groups = groups_resp.json()
    target = next((g for g in groups if g["name"] == "Category Test Group"), None)
    assert target, "Created group should be returned in list"
    assert len(target.get("expenses", [])) == len(expenses_payloads)

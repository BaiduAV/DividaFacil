#!/usr/bin/env python3
"""API group deletion tests using FastAPI TestClient."""

import pytest


@pytest.mark.usefixtures("client")
def test_delete_group_api(client):
    # Sign up (idempotent across runs)
    signup_payload = {
        "name": "Delete Test User",
        "email": "deletetest@example.com",
        "password": "testpass123",
    }
    signup_resp = client.post("/api/signup", json=signup_payload)
    assert signup_resp.status_code in (201, 400)

    # Login
    login_resp = client.post(
        "/api/login", json={"email": signup_payload["email"], "password": signup_payload["password"]}
    )
    assert login_resp.status_code == 200

    # Create a settled group and then delete it
    csrf_token = client.get("/api/csrf-token").json()["csrf_token"]
    group_resp = client.post(
        "/api/groups",
        headers={"X-CSRF-Token": csrf_token},
        json={"name": "Delete Test Group", "member_ids": [], "member_emails": []},
    )
    assert group_resp.status_code == 201
    group_id = group_resp.json()["id"]

    delete_resp = client.delete(
        f"/api/groups/{group_id}", headers={"X-CSRF-Token": csrf_token}
    )
    assert delete_resp.status_code == 204

    # Verify it's gone
    get_deleted = client.get(f"/api/groups/{group_id}")
    assert get_deleted.status_code == 404

    # Non-existent group delete
    missing_delete = client.delete("/api/groups/fake-group-id", headers={"X-CSRF-Token": csrf_token})
    assert missing_delete.status_code == 404

    # Ensure additional members exist so expense creates real outstanding balances
    # Sign up two extra users if not already existing
    for extra_email in ["alice@test.com", "bob@test.com"]:
        client.post("/api/signup", json={"name": extra_email.split("@")[0].title(), "email": extra_email, "password": "pass1234"})

    # Create group with members (by email) and add expense to make it unsettled
    group2_resp = client.post(
        "/api/groups",
        headers={"X-CSRF-Token": csrf_token},
        json={
            "name": "Unsettled Test Group",
            "member_ids": [],
            "member_emails": ["alice@test.com", "bob@test.com"],
        },
    )
    # Emails may not map to users if they don't exist; creation still succeeds with just current user
    assert group2_resp.status_code == 201
    group2 = group2_resp.json()
    group2_id = group2["id"]
    member_ids = list(group2["members"].keys())
    assert member_ids, "Group should have at least the creator as member"

    expense_payload = {
        "description": "Test Dinner for API",
        "amount": 150.0,
        "paid_by": member_ids[0],
        "split_type": "EQUAL",
        "split_among": member_ids,
    }
    expense_resp = client.post(
        f"/api/groups/{group2_id}/expenses", headers={"X-CSRF-Token": csrf_token}, json=expense_payload
    )
    assert expense_resp.status_code == 201

    # Attempt to delete unsettled group should fail with 400
    delete_unsettled = client.delete(
        f"/api/groups/{group2_id}", headers={"X-CSRF-Token": csrf_token}
    )
    assert delete_unsettled.status_code == 400
    detail = delete_unsettled.json().get("detail", "")
    assert "outstanding" in detail.lower()

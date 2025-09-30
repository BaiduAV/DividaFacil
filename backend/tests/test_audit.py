#!/usr/bin/env python3
"""Audit log tests.

We verify that creating a group and adding an expense writes audit events.
"""
import json
import os
import tempfile
from pathlib import Path

import pytest

from src import audit as audit_module


@pytest.fixture(autouse=True)
def temp_audit_log(monkeypatch):
    with tempfile.TemporaryDirectory() as tmp:
        log_path = Path(tmp) / "audit_test.log"
        # Monkeypatch module-level path
        monkeypatch.setattr(audit_module, "_AUDIT_PATH", str(log_path))
        yield log_path


def _signup_and_login(client, email):
    client.post("/api/signup", json={"name": "Audit User", "email": email, "password": "strongpass"})
    client.post("/api/login", json={"email": email, "password": "strongpass"})


def test_audit_group_and_expense_events(client, temp_audit_log):
    _signup_and_login(client, "audit_user@example.com")

    # CSRF token
    token = client.get("/api/csrf-token").json()["csrf_token"]

    # Create group
    g_resp = client.post(
        "/api/groups",
        headers={"X-CSRF-Token": token},
        json={"name": "Audit Group", "member_ids": [], "member_emails": []},
    )
    assert g_resp.status_code == 201
    group_id = g_resp.json()["id"]

    # Create expense
    members = list(g_resp.json()["members"].keys())
    e_resp = client.post(
        f"/api/groups/{group_id}/expenses",
        headers={"X-CSRF-Token": token},
        json={
            "description": "Audit Expense",
            "amount": 42.0,
            "paid_by": members[0],
            "split_type": "EQUAL",
            "split_among": members,
            "installments_count": 1,
        },
    )
    assert e_resp.status_code == 201

    # Read audit log
    content = temp_audit_log.read_text(encoding="utf-8").strip().splitlines()
    events = [json.loads(line) for line in content]

    # Expect at least 2 events
    event_names = {e["event"] for e in events}
    assert "group.created" in event_names
    assert "expense.created" in event_names

    for e in events:
        assert "ts" in e and e["ts"].endswith("Z") is False  # ISO includes offset
        assert e["actor_id"] is not None
        assert isinstance(e["details"], dict)

#!/usr/bin/env python3
"""Tests for CSRF protection middleware."""

import pytest

CSRF_ENDPOINT = "/api/csrf-token"
SIGNUP_ENDPOINT = "/api/signup"
LOGIN_ENDPOINT = "/api/login"
GROUPS_ENDPOINT = "/api/groups"


@pytest.fixture
def auth_client(client):
    # Create user + login to establish session for CSRF tests
    payload = {"name": "CSRF User", "email": "csrf_user@example.com", "password": "strongpass"}
    client.post(SIGNUP_ENDPOINT, json=payload)
    client.post(LOGIN_ENDPOINT, json={"email": payload["email"], "password": payload["password"]})
    return client


def test_missing_csrf_token_rejected(auth_client):
    # POST without token should fail 403
    resp = auth_client.post(GROUPS_ENDPOINT, json={"name": "NoToken", "member_ids": [], "member_emails": []})
    assert resp.status_code == 403
    assert "csrf" in resp.json().get("detail", "").lower()


def test_valid_csrf_token_allows_request(auth_client):
    # Fetch token
    token_resp = auth_client.get(CSRF_ENDPOINT)
    assert token_resp.status_code == 200
    token = token_resp.json()["csrf_token"]

    # Use token in header
    resp = auth_client.post(
        GROUPS_ENDPOINT,
        headers={"X-CSRF-Token": token},
        json={"name": "WithToken", "member_ids": [], "member_emails": []},
    )
    assert resp.status_code == 201


def test_invalid_csrf_token_rejected(auth_client):
    # Fetch real token to ensure session exists but send wrong one
    token_resp = auth_client.get(CSRF_ENDPOINT)
    assert token_resp.status_code == 200
    resp = auth_client.post(
        GROUPS_ENDPOINT,
        headers={"X-CSRF-Token": "bogus-token"},
        json={"name": "BadToken", "member_ids": [], "member_emails": []},
    )
    assert resp.status_code == 403
    assert "invalid" in resp.json().get("detail", "").lower()

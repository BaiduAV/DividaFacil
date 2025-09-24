from fastapi.testclient import TestClient

import web_app
from src.state import USERS, GROUPS  # Import from correct module


def test_add_user_and_group_flow(client: TestClient):
    # Add user
    resp = client.post("/users", data={"name": "Ana", "email": "ana@example.com"}, follow_redirects=False)
    assert resp.status_code in (303, 307)

    # Add another user
    resp = client.post("/users", data={"name": "Beto", "email": "beto@example.com"}, follow_redirects=False)
    assert resp.status_code in (303, 307)

    # Create group with both users
    users = list(USERS.values())
    data = {"name": "Viagem", "member_ids": [u.id for u in users]}
    resp = client.post("/groups", data=data, follow_redirects=False)
    assert resp.status_code in (303, 307)

    # Open the created group
    group_id = list(GROUPS.keys())[0]
    resp = client.get(f"/groups/{group_id}")
    assert resp.status_code == 200


def test_add_expense_with_comma_exact_and_percentage(authenticated_client: TestClient):
    client = authenticated_client
    # Setup: another user and a group
    client.post("/users", data={"name": "Beto", "email": "beto@example.com"})
    users = list(USERS.values())
    client.post("/groups", data={"name": "G", "member_ids": [u.id for u in users]})
    gid = list(GROUPS.keys())[0]

    # EXACT with comma values
    data = {
        "description": "Jantar",
        "amount": 31.0,
        "paid_by": users[0].id,
        "split_type": "EXACT",
        "split_among": [u.id for u in users],
        f"value_{users[0].id}": "10,50",
        f"value_{users[1].id}": "20,50",
    }
    r = client.post(f"/groups/{gid}/expenses", data=data, follow_redirects=False)
    assert r.status_code in (303, 307)

    # PERCENTAGE with comma values and invalid sum -> should 400 render page with error
    data = {
        "description": "Almoço",
        "amount": 100.0,
        "paid_by": users[0].id,
        "split_type": "PERCENTAGE",
        "split_among": [u.id for u in users],
        f"value_{users[0].id}": "30,0",
        f"value_{users[1].id}": "60,0",  # total 90 -> error
    }
    r = client.post(f"/groups/{gid}/expenses", data=data, follow_redirects=False)
    assert r.status_code == 400
    assert b"percentuais devem somar 100" in r.content


def test_installments_balance_recompute(authenticated_client: TestClient):
    client = authenticated_client
    # Setup: another user and a group
    client.post("/users", data={"name": "Beto", "email": "beto@example.com"})
    users = list(USERS.values())
    client.post("/groups", data={"name": "G", "member_ids": [u.id for u in users]})
    gid = list(GROUPS.keys())[0]

    # Add installment expense 3x 300, equal split
    data = {
        "description": "TV",
        "amount": 300.0,
        "paid_by": users[0].id,
        "split_type": "EQUAL",
        "installments_count": 3,
        "first_due_date": "2025-01-10",
        "split_among": [u.id for u in users],
    }
    r = client.post(f"/groups/{gid}/expenses", data=data, follow_redirects=False)
    assert r.status_code in (303, 307)

    # Pay first installment
    exp = web_app.GROUPS[gid].expenses[0]
    r = client.post(f"/groups/{gid}/expenses/{exp.id}/installments/1/pay", follow_redirects=False)
    assert r.status_code in (303, 307)

    # Re-open group and ensure balances reflect unpaid ratio (2/3 of equal share)
    resp = client.get(f"/groups/{gid}")
    assert resp.status_code == 200
    # Get fresh user objects from state after payment to see updated balances
    updated_users = list(web_app.USERS.values())
    u0 = updated_users[0] if updated_users[0].id == users[0].id else updated_users[1]
    u1 = updated_users[1] if updated_users[1].id == users[1].id else updated_users[0]
    # Compute remaining expected per user: total share (150) * (2/3) = 100
    assert round(u0.balance.get(u1.id, 0), 2) == 100.0
    assert round(u1.balance.get(u0.id, 0), 2) == -100.0


def test_percentage_boundary_api_pass_and_fail(authenticated_client: TestClient):
    client = authenticated_client
    # Setup: another user and a group
    client.post("/users", data={"name": "Beto", "email": "beto@example.com"})
    users = list(USERS.values())
    client.post("/groups", data={"name": "G", "member_ids": [u.id for u in users]})
    gid = list(GROUPS.keys())[0]

    # 100.01 -> should PASS (tolerance is > 0.01 to fail)
    data_ok = {
        "description": "Pct OK",
        "amount": 100.0,
        "paid_by": users[0].id,
        "split_type": "PERCENTAGE",
        "split_among": [u.id for u in users],
        f"value_{users[0].id}": "50.01",
        f"value_{users[1].id}": "49.99",
    }
    r = client.post(f"/groups/{gid}/expenses", data=data_ok, follow_redirects=False)
    assert r.status_code in (303, 307)

    # 100.02 -> should FAIL (abs diff > 0.01)
    data_bad = {
        "description": "Pct BAD",
        "amount": 100.0,
        "paid_by": users[0].id,
        "split_type": "PERCENTAGE",
        "split_among": [u.id for u in users],
        f"value_{users[0].id}": "50.02",
        f"value_{users[1].id}": "50.00",
    }
    r = client.post(f"/groups/{gid}/expenses", data=data_bad, follow_redirects=False)
    assert r.status_code == 400
    assert b"percentuais devem somar 100" in r.content


def test_invalid_split_value_format_returns_400(authenticated_client: TestClient):
    client = authenticated_client
    # Setup: another user and a group
    client.post("/users", data={"name": "Beto", "email": "beto@example.com"})
    users = list(USERS.values())
    client.post("/groups", data={"name": "G2", "member_ids": [u.id for u in users]})
    gid = list(GROUPS.keys())[0]

    data = {
        "description": "Bad value",
        "amount": 10.0,
        "paid_by": users[0].id,
        "split_type": "EXACT",
        "split_among": [u.id for u in users],
        f"value_{users[0].id}": "5,00",
        f"value_{users[1].id}": "abc",  # invalid
    }
    r = client.post(f"/groups/{gid}/expenses", data=data, follow_redirects=False)
    assert r.status_code == 400
    # Contains 'inválido' (UTF-8) from 'Número inválido para o usuário'
    assert b"inv\xc3\xa1lido" in r.content


def test_single_member_group_expense_flow(authenticated_client: TestClient):
    # Use the authenticated user as the single member
    client = authenticated_client
    users = list(web_app.USERS.values())
    solo = users[0]  # Use the authenticated user
    client.post("/groups", data={"name": "SoloG", "member_ids": [solo.id]})
    gid = list(web_app.GROUPS.keys())[0]

    data = {
        "description": "Solo expense",
        "amount": 123.45,
        "paid_by": solo.id,
        "split_type": "EQUAL",
        "split_among": [solo.id],
    }
    r = client.post(f"/groups/{gid}/expenses", data=data, follow_redirects=False)
    assert r.status_code in (303, 307)
    # Open group, there should be no inter-user balances
    resp = client.get(f"/groups/{gid}")
    assert resp.status_code == 200

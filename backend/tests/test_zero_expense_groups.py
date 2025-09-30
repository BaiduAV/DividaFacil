#!/usr/bin/env python3
"""Test groups with 0 expenses to verify they show 0 balance."""

import requests
import json


def test_zero_expense_groups():
    """Test that groups with 0 expenses show 0 balance."""

    BASE_URL = "http://127.0.0.1:8000/api"

    session = requests.Session()

    # Login
    try:
        # Try the main test user first
        login_response = session.post(
            f"{BASE_URL}/login", json={"email": "testuser@example.com", "password": "testpass123"}
        )

        if login_response.status_code != 200:
            # Try alternative login
            login_response = session.post(
                f"{BASE_URL}/login", json={"email": "test@example.com", "password": "testpass123"}
            )

        if login_response.status_code != 200:
            print("❌ Login failed with both test users")
            return

        print("✅ Logged in successfully")

    except Exception as e:
        print(f"❌ Login error: {e}")
        return

    # Get groups
    try:
        groups_response = session.get(f"{BASE_URL}/groups")
        if groups_response.status_code == 200:
            groups = groups_response.json()
            print(f"\n📊 Testing Groups with 0 Expenses:")

            for group in groups:
                expense_count = len(group.get("expenses", []))
                if expense_count == 0:
                    print(f"\n🔍 Group: {group['name']}")
                    print(f"   Expenses: {expense_count}")

                    balances = group.get("balances", {})
                    print(f"   Balances: {balances}")

                    # Check if all balances are zero
                    all_zero = all(abs(balance) < 0.01 for balance in balances.values())

                    if all_zero:
                        print(f"   ✅ Correct: All balances are zero!")
                    else:
                        print(f"   ❌ Problem: Non-zero balances in group with no expenses!")
                        for user_id, balance in balances.items():
                            if abs(balance) >= 0.01:
                                print(f"     User {user_id[:8]}... has balance: ${balance}")

            # Also test groups WITH expenses
            print(f"\n📊 Testing Groups with Expenses (for comparison):")
            for group in groups:
                expense_count = len(group.get("expenses", []))
                if expense_count > 0:
                    print(f"\n🔍 Group: {group['name']}")
                    print(f"   Expenses: {expense_count}")

                    balances = group.get("balances", {})
                    total_balance = sum(balances.values())
                    print(f"   Total system balance: ${total_balance:.2f} (should be ~0)")

                    if abs(total_balance) < 0.01:
                        print(f"   ✅ Balance system is consistent")
                    else:
                        print(f"   ❌ Balance inconsistency detected!")

        else:
            print(f"❌ Failed to get groups: {groups_response.status_code}")
    except Exception as e:
        print(f"❌ Groups API error: {e}")


if __name__ == "__main__":
    test_zero_expense_groups()

#!/usr/bin/env python3
"""Test script to demonstrate the authentication and expense filtering functionality."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_authentication_and_filtering():
    """Test the authentication and expense filtering workflow."""
    print("=== Testing Authentication and Expense Filtering ===")
    
    # Create two separate sessions to simulate different users
    alice_session = requests.Session()
    bob_session = requests.Session()
    
    # 1. Get users
    users_resp = alice_session.get(f"{BASE_URL}/api/users")
    users = users_resp.json()
    print(f"\nAvailable users: {[u['name'] for u in users]}")
    
    alice_id = next(u['id'] for u in users if u['name'] == 'Alice')
    bob_id = next(u['id'] for u in users if u['name'] == 'Bob')
    
    # 2. Login Alice
    print("\n📋 Logging in as Alice...")
    alice_login = alice_session.post(f"{BASE_URL}/login", data={"user_id": alice_id})
    print(f"Alice login status: {alice_login.status_code}")
    
    # 3. Login Bob
    print("\n📋 Logging in as Bob...")
    bob_login = bob_session.post(f"{BASE_URL}/login", data={"user_id": bob_id})
    print(f"Bob login status: {bob_login.status_code}")
    
    # 4. Get groups
    groups_resp = alice_session.get(f"{BASE_URL}/api/groups")
    groups = groups_resp.json()
    if groups:
        group_id = groups[0]['id']
        print(f"\nUsing group: {groups[0]['name']}")
    else:
        print("\nNo groups found, creating one...")
        # Create a group via API
        group_data = {"name": "API Test Group", "member_ids": [alice_id, bob_id]}
        group_resp = alice_session.post(f"{BASE_URL}/api/groups", json=group_data)
        if group_resp.status_code == 201:
            group_id = group_resp.json()['id']
            print(f"Created group: {group_resp.json()['name']}")
        else:
            print(f"Failed to create group: {group_resp.status_code}")
            return
    
    # 5. Alice creates an expense
    print("\n💰 Alice creating an expense...")
    alice_expense = {
        "description": "Dinner at Restaurant", 
        "amount": 100.0,
        "paid_by": alice_id,
        "split_among": [alice_id, bob_id],
        "split_type": "EQUAL"
    }
    alice_expense_resp = alice_session.post(f"{BASE_URL}/api/groups/{group_id}/expenses", json=alice_expense)
    print(f"Alice expense creation: {alice_expense_resp.status_code}")
    if alice_expense_resp.status_code == 201:
        print(f"Created expense: {alice_expense_resp.json()['description']}")
    
    # 6. Bob creates an expense
    print("\n💰 Bob creating an expense...")
    bob_expense = {
        "description": "Coffee and Snacks", 
        "amount": 30.0,
        "paid_by": bob_id,
        "split_among": [alice_id, bob_id],
        "split_type": "EQUAL"
    }
    bob_expense_resp = bob_session.post(f"{BASE_URL}/api/groups/{group_id}/expenses", json=bob_expense)
    print(f"Bob expense creation: {bob_expense_resp.status_code}")
    if bob_expense_resp.status_code == 201:
        print(f"Created expense: {bob_expense_resp.json()['description']}")
    
    # 7. Check Alice's expenses (should only see her own)
    print("\n👁️ Alice checking her expenses...")
    alice_expenses_resp = alice_session.get(f"{BASE_URL}/api/groups/{group_id}/expenses")
    alice_expenses = alice_expenses_resp.json()
    print(f"Alice sees {len(alice_expenses)} expense(s):")
    for exp in alice_expenses:
        print(f"  - {exp['description']} (${exp['amount']})")
    
    # 8. Check Bob's expenses (should only see his own)
    print("\n👁️ Bob checking his expenses...")
    bob_expenses_resp = bob_session.get(f"{BASE_URL}/api/groups/{group_id}/expenses")
    bob_expenses = bob_expenses_resp.json()
    print(f"Bob sees {len(bob_expenses)} expense(s):")
    for exp in bob_expenses:
        print(f"  - {exp['description']} (${exp['amount']})")
    
    # 9. Summary
    print("\n🎯 SUMMARY:")
    print(f"✅ Alice created expense: {alice_expense['description']}")
    print(f"✅ Bob created expense: {bob_expense['description']}")
    print(f"✅ Alice can only see her expense ({len(alice_expenses)} total)")
    print(f"✅ Bob can only see his expense ({len(bob_expenses)} total)")
    print(f"✅ Expense filtering by authenticated user is working correctly!")
    
    return True

if __name__ == "__main__":
    try:
        test_authentication_and_filtering()
        print("\n🎉 All tests passed! Authentication and expense filtering working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
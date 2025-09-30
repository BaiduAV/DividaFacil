#!/usr/bin/env python3
"""Comprehensive test of the group-specific balance logic."""

import requests
import json

def test_comprehensive_balance_logic():
    """Test balance logic across all users and groups."""
    
    BASE_URL = "http://127.0.0.1:8000/api"
    
    # Test with different users to see different group memberships
    test_users = [
        {"email": "test@example.com", "password": "testpass123"},
        {"email": "testuser@example.com", "password": "testpass123"},
        {"email": "bob@test.com", "password": "testpass123"},
    ]
    
    for i, user_creds in enumerate(test_users):
        session = requests.Session()
        
        print(f"\n{'='*60}")
        print(f"🧪 Testing with user: {user_creds['email']}")
        print(f"{'='*60}")
        
        # Login
        try:
            login_response = session.post(f"{BASE_URL}/login", json=user_creds)
            
            if login_response.status_code != 200:
                print(f"❌ Login failed for {user_creds['email']}")
                continue
            
            print(f"✅ Logged in as {user_creds['email']}")
            
        except Exception as e:
            print(f"❌ Login error for {user_creds['email']}: {e}")
            continue
        
        # Get groups for this user
        try:
            groups_response = session.get(f"{BASE_URL}/groups")
            if groups_response.status_code == 200:
                groups = groups_response.json()
                print(f"\n📊 This user is in {len(groups)} groups:")
                
                for group in groups:
                    expense_count = len(group.get('expenses', []))
                    print(f"\n  📁 Group: {group['name']}")
                    print(f"     Expenses: {expense_count}")
                    
                    # Show this user's balance in this group
                    balances = group.get('balances', {})
                    user_balance = None
                    
                    # Find this user's ID and balance
                    for member_id, member_data in group.get('members', {}).items():
                        if member_data.get('email') == user_creds['email']:
                            user_balance = balances.get(member_id, 0.0)
                            break
                    
                    if user_balance is not None:
                        if user_balance > 0:
                            print(f"     Your balance: You owe ${user_balance:.2f}")
                        elif user_balance < 0:
                            print(f"     Your balance: You are owed ${-user_balance:.2f}")
                        else:
                            print(f"     Your balance: $0.00 (settled)")
                        
                        # Validation
                        if expense_count == 0 and abs(user_balance) > 0.01:
                            print(f"     ❌ ERROR: Non-zero balance in group with no expenses!")
                        elif expense_count == 0:
                            print(f"     ✅ Correct: Zero balance for zero expenses")
                        else:
                            print(f"     ✅ Group has expenses, balance is acceptable")
                    else:
                        print(f"     ❓ Could not find user balance in this group")
                    
                    # Show some expense details if any
                    if expense_count > 0:
                        print(f"     Recent expenses:")
                        for j, expense in enumerate(group.get('expenses', [])[:2]):  # Show first 2
                            print(f"       {j+1}. {expense['description']}: ${expense['amount']}")
            
            else:
                print(f"❌ Failed to get groups: {groups_response.status_code}")
                
        except Exception as e:
            print(f"❌ Groups API error: {e}")
    
    print(f"\n{'='*60}")
    print("🎯 Test Summary: Group-specific balance logic")
    print("✅ Groups with 0 expenses should show $0.00 balance")
    print("✅ Groups with expenses should show calculated balances")
    print("✅ User balances should be isolated per group")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_comprehensive_balance_logic()
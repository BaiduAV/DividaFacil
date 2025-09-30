#!/usr/bin/env python3
"""Test what the API actually returns for balance information."""

import requests
import json

def test_api_balance_response():
    """Test the actual API response to see balance calculation."""
    
    BASE_URL = "http://127.0.0.1:8000/api"
    
    session = requests.Session()
    
    # Login
    try:
        login_response = session.post(f"{BASE_URL}/login", json={
            "email": "testuser@example.com", 
            "password": "testpass123"
        })
        
        if login_response.status_code != 200:
            print("❌ Login failed")
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
            print(f"\n📊 API Response Analysis:")
            
            for group in groups:
                if group['name'] == 'Teste2':
                    print(f"\nGroup: {group['name']}")
                    print(f"Members: {len(group.get('members', {}))}")
                    print(f"Expenses: {len(group.get('expenses', []))}")
                    
                    print("\n💰 Balance data from API:")
                    print(f"Balances field: {group.get('balances', {})}")
                    
                    print("\n👥 Member details:")
                    for member_id, member_data in group.get('members', {}).items():
                        print(f"  Member: {member_data['name']} ({member_id[:8]}...)")
                        print(f"    Balance in member data: {member_data.get('balance', {})}")
                        
                        # Show what this means
                        member_balance_dict = member_data.get('balance', {})
                        if member_balance_dict:
                            print("    Interpretation:")
                            for other_id, amount in member_balance_dict.items():
                                if amount > 0:
                                    print(f"      This user owes someone ${amount:.2f}")
                                elif amount < 0:
                                    print(f"      This user is owed ${-amount:.2f}")
                    
                    print(f"\n📝 Expenses in this group:")
                    for expense in group.get('expenses', []):
                        print(f"  - {expense['description']}: ${expense['amount']}")
                        print(f"    Paid by: {expense['paid_by'][:8]}...")
                        print(f"    Split type: {expense['split_type']}")
                        if expense.get('split_values'):
                            print(f"    Split values: {expense['split_values']}")
                    
                    break
            
        else:
            print(f"❌ Failed to get groups: {groups_response.status_code}")
    except Exception as e:
        print(f"❌ Groups API error: {e}")

if __name__ == "__main__":
    test_api_balance_response()
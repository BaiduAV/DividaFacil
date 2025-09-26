#!/usr/bin/env python3
"""Add test user to Category Test Group and verify expenses display."""

import requests
import json


def test_category_display():
    """Test the complete category functionality flow."""
    
    base_url = "http://localhost:8000"
    
    # Login
    login_data = {
        "email": "tester@example.com",
        "password": "test123"
    }
    
    session = requests.Session()
    
    print("🔐 Logging in...")
    response = session.post(f"{base_url}/api/login", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code} - {response.text}")
        return
    
    print("✅ Login successful!")
    
    # Add user to Category Test Group
    group_id = "8a1c300b-e64c-492e-b874-c4d5704832c4"  # Category Test Group ID
    user_id = "6999e981-0ef0-464d-b831-c59699ea0239"   # Test user ID from previous test
    
    print(f"\n👥 Adding user to group {group_id}...")
    response = session.post(f"{base_url}/api/groups/{group_id}/members/{user_id}")
    if response.status_code == 204:
        print("✅ Successfully added to group!")
    elif response.status_code == 409:
        print("ℹ️  User already in group")
    else:
        print(f"⚠️  Add to group result: {response.status_code} - {response.text}")
    
    # Now get groups to verify
    print("\n📁 Getting groups...")
    response = session.get(f"{base_url}/api/groups")
    if response.status_code == 200:
        groups = response.json()
        print(f"✅ Found {len(groups)} groups")
        
        for group in groups:
            if group.get('name') == 'Category Test Group':
                print(f"\n🎯 Found Category Test Group!")
                print(f"   Group ID: {group.get('id')}")
                print(f"   Members: {len(group.get('members', {}))}")
                
                expenses = group.get('expenses', [])
                print(f"   💰 Expenses: {len(expenses)}")
                
                # Check category distribution
                category_counts = {}
                for expense in expenses:
                    category = expense.get('category') or 'None/General'
                    category_counts[category] = category_counts.get(category, 0) + 1
                    print(f"      - {expense.get('description')}: ${expense.get('amount'):.2f} (Category: {category})")
                
                print(f"\n📊 Category Summary:")
                for category, count in category_counts.items():
                    print(f"      {category}: {count} expense(s)")
                
                break
    else:
        print(f"❌ Groups request failed: {response.status_code} - {response.text}")


if __name__ == "__main__":
    test_category_display()
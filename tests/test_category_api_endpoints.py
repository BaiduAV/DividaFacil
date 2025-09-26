#!/usr/bin/env python3
"""Test authentication and category API endpoints."""

import requests
import json


def test_category_api_endpoints():
    """Test the category functionality through API endpoints."""
    
    base_url = "http://localhost:8000"
    
    # Test 1: Check health
    print("🏥 Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/healthz")
        print(f"✓ Health check: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return
    
    # Test 2: Try to register a test user
    print("\n👤 Testing user registration...")
    test_user = {
        "name": "Test User",
        "email": "test@example.com", 
        "password": "testpass123"
    }
    
    try:
        response = requests.post(f"{base_url}/api/users", json=test_user)
        if response.status_code in [200, 201]:
            print(f"✓ User registration: {response.status_code}")
            user_data = response.json()
            print(f"  User ID: {user_data.get('id')}")
        elif response.status_code == 400:
            print("ℹ️ User might already exist, continuing...")
        else:
            print(f"⚠️ User registration: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ User registration failed: {e}")
    
    # Test 3: Try to login
    print("\n🔐 Testing login...")
    login_data = {
        "email": test_user["email"],
        "password": test_user["password"]
    }
    
    session = requests.Session()
    try:
        response = session.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print(f"✓ Login successful: {response.status_code}")
            auth_data = response.json()
            
            # Store token if provided
            if "access_token" in auth_data:
                token = auth_data["access_token"]
                session.headers.update({"Authorization": f"Bearer {token}"})
                print(f"  Token stored: {token[:20]}...")
        else:
            print(f"⚠️ Login failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Login failed: {e}")
    
    # Test 4: Get groups
    print("\n📁 Testing groups endpoint...")
    try:
        response = session.get(f"{base_url}/api/groups")
        if response.status_code == 200:
            groups = response.json()
            print(f"✓ Groups retrieved: {len(groups)} groups found")
            
            for i, group in enumerate(groups[:3]):  # Show first 3 groups
                print(f"  Group {i+1}: {group.get('name')} (ID: {group.get('id')})")
                
                # Test expenses for this group
                if 'expenses' in group and group['expenses']:
                    print(f"    📝 {len(group['expenses'])} expenses:")
                    for expense in group['expenses'][:2]:  # Show first 2 expenses
                        category = expense.get('category', 'None')
                        print(f"      - {expense.get('description')}: ${expense.get('amount'):.2f} (Category: {category})")
        else:
            print(f"⚠️ Groups request: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Groups request failed: {e}")
    
    # Test 5: Get expenses directly
    print("\n💰 Testing expenses endpoint...")
    try:
        response = session.get(f"{base_url}/api/expenses")
        if response.status_code == 200:
            expenses = response.json()
            print(f"✓ Expenses retrieved: {len(expenses)} expenses found")
            
            category_counts = {}
            for expense in expenses:
                category = expense.get('category') or 'None'
                category_counts[category] = category_counts.get(category, 0) + 1
                
            print("  📊 Category breakdown:")
            for category, count in category_counts.items():
                print(f"    - {category}: {count} expense(s)")
                
        else:
            print(f"⚠️ Expenses request: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Expenses request failed: {e}")


if __name__ == "__main__":
    test_category_api_endpoints()
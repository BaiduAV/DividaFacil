#!/usr/bin/env python3
"""Create a test user and login to test the category functionality."""

import requests
import json


def create_and_test_user():
    """Create a test user and verify login works."""
    
    base_url = "http://localhost:8000"
    
    # Create test user
    user_data = {
        "name": "Category Tester",
        "email": "tester@example.com",
        "password": "test123"
    }
    
    print("🔧 Creating test user...")
    try:
        response = requests.post(f"{base_url}/api/signup", json=user_data)
        if response.status_code in [200, 201]:
            print(f"✅ User created successfully: {response.json()}")
        elif response.status_code == 409:
            print("ℹ️  User already exists, proceeding with login...")
        else:
            print(f"❌ User creation failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error creating user: {e}")
        return
    
    # Test login
    print("\n🔐 Testing login...")
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    session = requests.Session()
    try:
        response = session.post(f"{base_url}/api/login", json=login_data)
        if response.status_code == 200:
            auth_response = response.json()
            print(f"✅ Login successful!")
            print(f"   User ID: {auth_response.get('id')}")
            print(f"   Name: {auth_response.get('name')}")
            print(f"   Email: {auth_response.get('email')}")
            
            # Check if there's a token
            if 'token' in auth_response:
                session.headers.update({"Authorization": f"Bearer {auth_response['token']}"})
                
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Login error: {e}")
        return
    
    # Test groups access
    print("\n📁 Testing groups access...")
    try:
        response = session.get(f"{base_url}/api/groups")
        print(f"Groups endpoint status: {response.status_code}")
        if response.status_code == 200:
            groups = response.json()
            print(f"✅ Found {len(groups)} groups")
            for group in groups[:2]:
                print(f"   - {group.get('name')} ({group.get('id')})")
                if 'expenses' in group:
                    print(f"     📝 {len(group['expenses'])} expenses")
        else:
            print(f"❌ Groups access failed: {response.text}")
    except Exception as e:
        print(f"❌ Groups access error: {e}")


if __name__ == "__main__":
    create_and_test_user()
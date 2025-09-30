#!/usr/bin/env python3
"""Test script to verify the API returns correct group data."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_groups_api_response():
    """Test if the groups API returns correct expense association."""
    
    print("=== Groups API Response Test ===\n")
    
    # Start the backend server first if not running
    print("Testing if backend is running...")
    try:
        health_response = requests.get("http://127.0.0.1:8000/healthz", timeout=5)
        if health_response.status_code == 200:
            print("✅ Backend is running")
        else:
            print("❌ Backend not responding properly")
            return
    except Exception as e:
        print("❌ Backend not running - please start with: uvicorn web_app:app --reload")
        return
    
    # Create a session for authentication
    session = requests.Session()
    
    # Login with existing user
    print("\n1. Logging in...")
    login_data = {"email": "testuser@example.com", "password": "testpass123"}
    
    try:
        login_response = session.post(f"{BASE_URL}/login", json=login_data)
        if login_response.status_code == 200:
            print("   ✅ Login successful")
        else:
            print(f"   ❌ Login failed: {login_response.status_code} - {login_response.text}")
            return
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return
    
    # Get all groups
    print("\n2. Fetching groups...")
    try:
        groups_response = session.get(f"{BASE_URL}/groups")
        if groups_response.status_code == 200:
            groups = groups_response.json()
            print(f"   ✅ Retrieved {len(groups)} groups")
            
            print("\n3. Group details:")
            for i, group in enumerate(groups):
                print(f"   Group {i+1}: {group['name']} (ID: {group['id'][:8]}...)")
                print(f"     Members: {len(group.get('members', {}))}")
                print(f"     Expenses: {len(group.get('expenses', []))}")
                
                if group.get('expenses'):
                    print("     Expense details:")
                    for j, expense in enumerate(group['expenses']):
                        print(f"       {j+1}. {expense['description']} - ${expense['amount']}")
                print()
        else:
            print(f"   ❌ Failed to get groups: {groups_response.status_code} - {groups_response.text}")
            return
            
    except Exception as e:
        print(f"   ❌ Groups API error: {e}")
        return
    
    print("=== API Test completed ===")


if __name__ == "__main__":
    test_groups_api_response()
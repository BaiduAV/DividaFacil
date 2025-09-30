#!/usr/bin/env python3
"""Test script to verify the complete group deletion API flow."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_delete_group_api():
    """Test the complete API flow for group deletion."""
    
    print("=== Group Deletion API Test ===\n")
    
    # Create a session for authentication
    session = requests.Session()
    
    # Create and login test user
    print("1. Creating and logging in test user...")
    signup_data = {
        "name": "Delete Test User",
        "email": "deletetest@example.com",
        "password": "testpass123"
    }
    
    try:
        signup_response = session.post(f"{BASE_URL}/signup", json=signup_data)
        if signup_response.status_code == 409:
            print("   User already exists, proceeding to login...")
        elif signup_response.status_code == 200:
            print("   User created successfully")
        else:
            print(f"   Signup failed: {signup_response.text}")
            
    except Exception as e:
        print(f"   Signup error: {e}")
        
    # Login
    login_data = {"email": "deletetest@example.com", "password": "testpass123"}
    login_response = session.post(f"{BASE_URL}/login", json=login_data)
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
        
    print("   Login successful!")
    
    # Create a test group
    print("\n2. Creating test group...")
    group_data = {
        "name": "Delete Test Group",
        "member_ids": [],
        "member_emails": []
    }
    
    create_response = session.post(f"{BASE_URL}/groups", json=group_data)
    if create_response.status_code != 201:
        print(f"   Group creation failed: {create_response.text}")
        return
        
    group = create_response.json()
    group_id = group['id']
    print(f"   Group created: {group['name']} (ID: {group_id})")
    print(f"   Members: {len(group['members'])}")
    
    # Test 1: Delete settled group (should work)
    print(f"\n3. Attempting to delete settled group...")
    delete_response = session.delete(f"{BASE_URL}/groups/{group_id}")
    print(f"   Delete response status: {delete_response.status_code}")
    
    if delete_response.status_code == 204:
        print("   ✅ Settled group deleted successfully!")
        
        # Verify deletion
        verify_response = session.get(f"{BASE_URL}/groups/{group_id}")
        print(f"   Verification - Group exists: {verify_response.status_code != 404}")
        
    else:
        print(f"   ❌ Delete failed: {delete_response.text}")
    
    # Test 2: Try to delete non-existent group
    print(f"\n4. Attempting to delete non-existent group...")
    fake_delete_response = session.delete(f"{BASE_URL}/groups/fake-group-id")
    print(f"   Status: {fake_delete_response.status_code}")
    if fake_delete_response.status_code == 404:
        print("   ✅ Correctly returned 404 for non-existent group")
    else:
        print(f"   Response: {fake_delete_response.text}")
    
    # Test 3: Create group with expenses (unsettled)
    print(f"\n5. Creating group with expenses (unsettled)...")
    
    # Create another group
    group_data2 = {
        "name": "Unsettled Test Group",
        "member_ids": [],
        "member_emails": ["alice@test.com", "bob@test.com"]  # Users from previous test
    }
    
    create_response2 = session.post(f"{BASE_URL}/groups", json=group_data2)
    if create_response2.status_code != 201:
        print(f"   Group creation failed: {create_response2.text}")
        return
        
    group2 = create_response2.json()
    group2_id = group2['id']
    print(f"   Group created: {group2['name']} (ID: {group2_id})")
    
    # Add an expense to make it unsettled
    expense_data = {
        "description": "Test Dinner for API",
        "amount": 150.00,
        "paid_by": list(group2['members'].keys())[0],  # First member pays
        "split_type": "EQUAL",
        "split_among": list(group2['members'].keys())
    }
    
    expense_response = session.post(f"{BASE_URL}/groups/{group2_id}/expenses", json=expense_data)
    if expense_response.status_code == 201:
        print("   Expense added successfully")
        
        # Try to delete unsettled group
        print(f"\n6. Attempting to delete unsettled group...")
        delete_unsettled_response = session.delete(f"{BASE_URL}/groups/{group2_id}")
        print(f"   Status: {delete_unsettled_response.status_code}")
        
        if delete_unsettled_response.status_code == 400:
            print("   ✅ Correctly blocked deletion of unsettled group")
            print(f"   Error message: {delete_unsettled_response.json().get('detail', 'No detail provided')}")
        else:
            print(f"   ❌ Unexpected response: {delete_unsettled_response.text}")
    else:
        print(f"   Failed to add expense: {expense_response.text}")
    
    print(f"\n=== API Test completed ===")


if __name__ == "__main__":
    test_delete_group_api()
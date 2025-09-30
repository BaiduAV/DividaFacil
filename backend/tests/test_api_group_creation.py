#!/usr/bin/env python3
"""Test script to simulate frontend group creation with emails."""

import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_api_group_creation():
    """Test the complete API flow for group creation with emails."""
    
    # First, create a test user account to get auth
    print("Creating test user account...")
    signup_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpass123"
    }
    
    try:
        signup_response = requests.post(f"{BASE_URL}/signup", json=signup_data)
        print(f"Signup response: {signup_response.status_code}")
        if signup_response.status_code == 200:
            print("Signup successful!")
        elif signup_response.status_code == 409:
            print("User already exists, continuing...")
        else:
            print(f"Signup failed: {signup_response.text}")
    except Exception as e:
        print(f"Signup error: {e}")
        
    # Login to get session
    print(f"\nLogging in...")
    login_data = {
        "email": "testuser@example.com", 
        "password": "testpass123"
    }
    
    try:
        # Create a session to maintain cookies
        session = requests.Session()
        login_response = session.post(f"{BASE_URL}/login", json=login_data)
        print(f"Login response: {login_response.status_code}")
        if login_response.status_code == 200:
            print("Login successful!")
        else:
            print(f"Login failed: {login_response.text}")
            return
            
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Test group creation with emails
    print(f"\nCreating group with email addresses...")
    group_data = {
        "name": "Test Group with Emails",
        "member_ids": [],  # Using existing user IDs if we had them
        "member_emails": ["alice@test.com", "bob@test.com", "nonexistent@test.com"]
    }
    
    try:
        create_response = session.post(f"{BASE_URL}/groups", json=group_data)
        print(f"Group creation response: {create_response.status_code}")
        if create_response.status_code == 201:
            group = create_response.json()
            print("Group created successfully!")
            print(f"Group name: {group['name']}")
            print(f"Group members: {len(group['members'])}")
            for member_id, member in group['members'].items():
                print(f"- {member['name']} ({member['email']})")
        else:
            print(f"Group creation failed: {create_response.text}")
            
    except Exception as e:
        print(f"Group creation error: {e}")
    
    # List groups to verify
    print(f"\nListing groups...")
    try:
        groups_response = session.get(f"{BASE_URL}/groups")
        print(f"List groups response: {groups_response.status_code}")
        if groups_response.status_code == 200:
            groups = groups_response.json()
            print(f"Total groups: {len(groups)}")
            for group in groups:
                print(f"- {group['name']} ({len(group['members'])} members)")
        else:
            print(f"Failed to list groups: {groups_response.text}")
            
    except Exception as e:
        print(f"List groups error: {e}")


if __name__ == "__main__":
    test_api_group_creation()
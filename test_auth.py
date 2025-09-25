#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_auth_flow():
    # Create a session to maintain cookies
    session = requests.Session()
    
    # 1. Test signup
    print("1. Testing signup...")
    signup_data = {
        "name": "Test User 2",
        "email": "test2@example.com",
        "password": "testpassword123"
    }
    
    response = session.post(f"{BASE_URL}/api/signup", json=signup_data)
    print(f"Signup status: {response.status_code}")
    if response.status_code != 201:
        print(f"Signup error: {response.text}")
    else:
        print("Signup successful!")
    
    # 2. Test login
    print("\n2. Testing login...")
    login_data = {
        "email": "test2@example.com",
        "password": "testpassword123"
    }
    
    response = session.post(f"{BASE_URL}/api/login", json=login_data)
    print(f"Login status: {response.status_code}")
    if response.status_code != 200:
        print(f"Login error: {response.text}")
    else:
        print("Login successful!")
        print(f"Response: {response.json()}")
    
    # 3. Test /users endpoint (current user)
    print("\n3. Testing /users endpoint...")
    response = session.get(f"{BASE_URL}/api/users")
    print(f"Users status: {response.status_code}")
    if response.status_code != 200:
        print(f"Users error: {response.text}")
    else:
        print("Users successful!")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    test_auth_flow()
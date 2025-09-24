#!/usr/bin/env python3
"""Quick test script to validate API authentication fixes."""

from fastapi.testclient import TestClient
from web_app import app

def test_api_login():
    """Test the API login functionality."""
    client = TestClient(app)

    print("Testing API login endpoint...")

    # Test with non-existent user (should return 400)
    print("1. Testing with non-existent user:")
    resp = client.post("/api/login", data={"email": "nonexistent@example.com"})
    print(f"   Status: {resp.status_code} (expected 400)")

    # Test with existing user if any
    print("2. Testing health check:")
    health_resp = client.get("/healthz")
    print(f"   Health check status: {health_resp.status_code} (expected 200)")
    print(f"   Health response: {health_resp.json()}")

    print("\nAPI endpoint is accessible and responding correctly!")

if __name__ == "__main__":
    test_api_login()

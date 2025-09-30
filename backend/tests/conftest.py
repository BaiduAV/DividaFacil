#!/usr/bin/env python3
"""Pytest configuration and fixtures for DividaFacil tests."""

import pytest
import uuid
from src.services.database_service import DatabaseService


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Set up test database before running tests."""
    # This runs once before all tests
    print("Setting up test database...")
    # We could create a separate test database here if needed
    yield
    # Cleanup after all tests (if needed)


@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test."""
    # This runs before each test
    yield
    # This runs after each test - could clean up test data here


@pytest.fixture
def unique_email():
    """Generate a unique email for testing."""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def test_user(unique_email):
    """Create a test user that gets cleaned up after the test."""
    user = DatabaseService.create_user("Test User", unique_email)
    yield user
    # Cleanup - could delete the user here if needed


@pytest.fixture
def test_users():
    """Create multiple test users."""
    users = []
    for i in range(3):
        email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        user = DatabaseService.create_user(f"Test User {i+1}", email)
        users.append(user)
    yield users
    # Cleanup could go here
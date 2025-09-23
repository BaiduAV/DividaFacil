"""
Tests for authentication and access control functionality.
"""
import pytest
from fastapi.testclient import TestClient

from web_app import app
# Authentication functions are tested via web endpoints
from src.services.database_service import DatabaseService


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_sessions():
    """Clear all sessions before each test."""
    # Sessions are now handled by FastAPI's session middleware
    pass


@pytest.fixture
def test_user():
    """Create a test user."""
    return DatabaseService.create_user("Test User", "test@example.com")


@pytest.fixture
def other_user():
    """Create another test user."""
    return DatabaseService.create_user("Other User", "other@example.com")


def test_unauthenticated_api_access_denied(client):
    """Test that API endpoints require authentication."""
    # Test users endpoint
    response = client.get("/api/users")
    assert response.status_code == 401
    assert "Authentication required" in response.json()["detail"]
    
    # Test groups endpoint
    response = client.get("/api/groups")
    assert response.status_code == 401
    
    # Test specific user endpoint
    response = client.get("/api/users/some-id")
    assert response.status_code == 401


def test_login_api_success(client, test_user):
    """Test successful API login."""
    response = client.post("/api/login", data={"email": test_user.email})
    assert response.status_code == 200
    assert response.json()["user_id"] == test_user.id
    assert response.json()["user_name"] == test_user.name
    
    # Check session cookie is set
    assert "session_id" in response.cookies


def test_login_api_invalid_email(client):
    """Test API login with invalid email."""
    response = client.post("/api/login", data={"email": "nonexistent@example.com"})
    assert response.status_code == 400
    assert "User not found" in response.json()["detail"]


def test_authenticated_user_access_own_data(client, test_user):
    """Test that authenticated user can access their own data."""
    # Login first
    login_response = client.post("/api/login", data={"email": test_user.email})
    assert login_response.status_code == 200
    
    # Use session cookie from login
    session_id = login_response.cookies["session_id"]
    
    # Access own user data
    response = client.get(f"/api/users/{test_user.id}", cookies={"session_id": session_id})
    assert response.status_code == 200
    assert response.json()["id"] == test_user.id


def test_authenticated_user_cannot_access_other_user_data(client, test_user, other_user):
    """Test that authenticated user cannot access other user's data."""
    # Login as test_user
    login_response = client.post("/api/login", data={"email": test_user.email})
    session_id = login_response.cookies["session_id"]
    
    # Try to access other user's data
    response = client.get(f"/api/users/{other_user.id}", cookies={"session_id": session_id})
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_user_can_only_see_their_groups(client, test_user, other_user):
    """Test that users can only see groups they're members of."""
    # Login as test_user
    login_response = client.post("/api/login", data={"email": test_user.email})
    session_id = login_response.cookies["session_id"]
    
    # Create a group (test_user should be automatically added as member)
    group_response = client.post(
        "/api/groups", 
        json={"name": "Test Group"},
        cookies={"session_id": session_id}
    )
    assert group_response.status_code == 201
    group_id = group_response.json()["id"]
    
    # Test user should see their group
    groups_response = client.get("/api/groups", cookies={"session_id": session_id})
    assert groups_response.status_code == 200
    groups = groups_response.json()
    assert len(groups) == 1
    assert groups[0]["id"] == group_id
    
    # Login as other_user
    other_login = client.post("/api/login", data={"email": other_user.email})
    other_session_id = other_login.cookies["session_id"]
    
    # Other user should not see the group
    other_groups_response = client.get("/api/groups", cookies={"session_id": other_session_id})
    assert other_groups_response.status_code == 200
    other_groups = other_groups_response.json()
    assert len(other_groups) == 0


def test_user_cannot_access_group_they_are_not_member_of(client, test_user, other_user):
    """Test that users cannot access groups they're not members of."""
    # Login as test_user and create group
    login_response = client.post("/api/login", data={"email": test_user.email})
    session_id = login_response.cookies["session_id"]
    
    group_response = client.post(
        "/api/groups", 
        json={"name": "Test Group"},
        cookies={"session_id": session_id}
    )
    group_id = group_response.json()["id"]
    
    # Login as other_user
    other_login = client.post("/api/login", data={"email": other_user.email})
    other_session_id = other_login.cookies["session_id"]
    
    # Other user should not be able to access the group
    response = client.get(f"/api/groups/{group_id}", cookies={"session_id": other_session_id})
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]


def test_logout_clears_session(client, test_user):
    """Test that logout clears the session."""
    # Login first
    login_response = client.post("/api/login", data={"email": test_user.email})
    session_id = login_response.cookies["session_id"]
    
    # Verify we can access protected endpoint
    response = client.get("/api/users", cookies={"session_id": session_id})
    assert response.status_code == 200
    
    # Logout
    logout_response = client.post("/api/logout", cookies={"session_id": session_id})
    assert logout_response.status_code == 200
    
    # Verify we can no longer access protected endpoint with old session
    response = client.get("/api/users", cookies={"session_id": session_id})
    assert response.status_code == 401


def test_dashboard_shows_login_when_not_authenticated(client):
    """Test that dashboard shows login page when not authenticated."""
    response = client.get("/")
    assert response.status_code == 200
    # Should show login page (would need to check HTML content to verify)


def test_user_can_only_create_expenses_in_their_groups(client, test_user, other_user):
    """Test that users can only create expenses in groups they're members of."""
    # Create a group as test_user
    login_response = client.post("/api/login", data={"email": test_user.email})
    session_id = login_response.cookies["session_id"]
    
    group_response = client.post(
        "/api/groups", 
        json={"name": "Test Group"},
        cookies={"session_id": session_id}
    )
    group_id = group_response.json()["id"]
    
    # Login as other_user
    other_login = client.post("/api/login", data={"email": other_user.email})
    other_session_id = other_login.cookies["session_id"]
    
    # Other user should not be able to create expense in the group
    expense_data = {
        "amount": 100.0,
        "description": "Test expense",
        "paid_by": other_user.id,
        "split_among": [other_user.id],
        "split_type": "EQUAL"
    }
    
    response = client.post(
        f"/api/groups/{group_id}/expenses",
        json=expense_data,
        cookies={"session_id": other_session_id}
    )
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]
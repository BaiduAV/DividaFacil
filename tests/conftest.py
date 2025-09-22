import pytest
import sys
import tempfile
import os
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure project root is in sys.path for module imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import web_app
from src.database import engine, Base


@pytest.fixture(autouse=True)
def reset_state():
    # Clear in-memory storages before each test
    web_app.USERS.clear()
    web_app.GROUPS.clear()
    # Clear database tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after test
    web_app.USERS.clear()
    web_app.GROUPS.clear()


@pytest.fixture()
def client():
    return TestClient(web_app.app)


@pytest.fixture()
def authenticated_client(client):
    """Return a test client with a user automatically logged in."""
    # Create a test user
    resp = client.post("/users", data={"name": "Test User", "email": "test@example.com"})
    
    # Get the created user
    users = list(web_app.USERS.values())
    if users:
        # Login the user
        resp = client.post("/login", data={"user_id": users[0].id})
        # Login redirects to dashboard, which should be accessible
        assert resp.status_code in (303, 307, 200)
    
    return client

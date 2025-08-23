import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Ensure project root is in sys.path for module imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import web_app


@pytest.fixture(autouse=True)
def reset_state():
    # Clear in-memory storages before each test
    web_app.USERS.clear()
    web_app.GROUPS.clear()
    yield
    web_app.USERS.clear()
    web_app.GROUPS.clear()


@pytest.fixture()
def client():
    return TestClient(web_app.app)

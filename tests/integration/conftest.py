import pytest
from src.app import users_app

@pytest.fixture
def client():
    users_app.config["TESTING"] = True
    with users_app.test_client() as client:
        yield client

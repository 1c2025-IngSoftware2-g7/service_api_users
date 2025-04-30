import pytest
from app import users_app


# Expose app to pytest:
@pytest.fixture
def app():
    return users_app


# This fixture forces all tests to run within the application context:
@pytest.fixture(autouse=True)
def app_context(app):
    with app.app_context():
        yield

import pytest
from unittest.mock import patch, MagicMock


# Mock for the database connection used in unit tests
@pytest.fixture(autouse=True)
def mock_db_connection():
    with patch("src.infrastructure.persistence.base_entity.psycopg.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        yield


# Expose app to pytest:
@pytest.fixture
def app(mock_db_connection):
    from app import users_app
    app = users_app
    app.secret_key = "test_secret_key"
    return app


# This fixture forces all tests to run within the application context:
@pytest.fixture(autouse=True)
def app_context(app):
    with app.app_context():
        yield


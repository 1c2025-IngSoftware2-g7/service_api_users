import os
import pytest
import requests
import time

BASE_URL = os.getenv("BASE_URL", "http://app:8080")

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


@pytest.fixture(scope="session", autouse=True)
def wait_for_app():
    """Espera a que la app esté viva antes de correr tests"""
    for _ in range(20):
        try:
            response = requests.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                break
        except Exception:
            pass
        time.sleep(3)
    else:
        raise RuntimeError("La API no está disponible.")

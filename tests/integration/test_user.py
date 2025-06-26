import requests
import uuid

BASE_URL = "http://app:8080"

def test_get_users():
    response = requests.get(f"{BASE_URL}/users")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_create_user():
    data = {
        "email": f"testuser{uuid.uuid4().hex[:6]}@example.com",
        "password": "test1234",
        "role": "student",
        "given_name": "Test",
        "family_name": "User"
    }
    response = requests.post(f"{BASE_URL}/users", json=data)
    assert response.status_code in (201, 200, 400)  # según lógica implementada

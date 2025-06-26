import requests

def test_login_admin_wrong_credentials():
    data = {"email": "wrong@example.com", "password": "incorrect"}
    response = requests.post("http://app:8080/users/admin/login", json=data)
    assert response.status_code in (401, 404)

def test_login_admin_missing_data():
    response = requests.post("http://app:8080/users/admin/login", json={})
    assert response.status_code == 400

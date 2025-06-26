import requests

def test_password_recovery_nonexistent_user():
    response = requests.post("http://app:8080/users/nonexistent@example.com/password-recovery")
    assert response.status_code == 404

def test_password_recovery_nonexistent_user(client):
    response = client.post("/users/nonexistent@example.com/password-recovery")
    assert response.status_code == 404

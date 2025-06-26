def test_login_admin_wrong_credentials(client):
    data = {"email": "wrong@example.com", "password": "incorrect"}
    response = client.post("/users/admin/login", json=data)
    assert response.status_code == 404

def test_login_admin_missing_data(client):
    response = client.post("/users/admin/login", json={})
    assert response.status_code == 400

def test_login_users_missing_data(client):
    response = client.post("/users/login", json={})
    assert response.status_code == 400
    assert isinstance(response.json, dict)

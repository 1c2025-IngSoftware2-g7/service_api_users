def test_get_users(client):
    response = client.get("/users")
    assert response.status_code == 200

    data = response.get_json()
    assert "data" in data
    assert isinstance(data["data"], list)

def test_create_user(client):
    data = {
        "name": "Test",
        "surname": "Test",
        "email": "test@gmail.com",
        "password": "1234",
        "status": "active",
        "role": "student",
        "notification": True
    }
    response = client.post("/users", json=data)
    assert response.status_code == 201

import uuid

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

def test_get_users_without_check_session(client):
    response = client.get("/users/admin")
    assert response.status_code == 200
    assert isinstance(response.json, dict)

def test_get_specific_users(client):
    fake_uuid = str(uuid.uuid4())
    response = client.get(f"/users/{fake_uuid}")
    assert response.status_code == 404
    assert isinstance(response.json, dict)

def test_get_specific_users_in_check(client):
    fake_uuid = str(uuid.uuid4())
    response = client.get(f"/users_check/{fake_uuid}")
    assert response.status_code == 404
    assert isinstance(response.json, dict)

def test_get_active_teachers(client):
    response = client.get("/users/teachers")
    assert response.status_code == 200
    assert isinstance(response.json, dict)

def test_delete_specific_users_not_found(client):
    fake_uuid = str(uuid.uuid4())
    response = client.delete(f"/users/{fake_uuid}")
    assert response.status_code == 404
    assert isinstance(response.json, dict)

def test_set_user_location_missing_body(client):
    fake_uuid = str(uuid.uuid4())
    response = client.put(f"/users/{fake_uuid}/location", json={})
    assert response.status_code == 400
    assert isinstance(response.json, dict)

def test_add_admin_missing_data(client):
    response = client.post("/users/admin", json={})
    assert response.status_code == 400
    assert isinstance(response.json, dict)

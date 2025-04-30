import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify
from presentation.user_controller import UserController
from werkzeug.security import generate_password_hash

from app import users_app

@pytest.fixture
def app():
    yield users_app

@pytest.fixture
def mock_user():
    class MockUser:
        def __init__(self):
            self.uuid = "1234"
            self.name = "Test"
            self.surname = "User"
            self.password = generate_password_hash("password")
            self.email = "user.test@gmail.com"
            self.status = "enabled"
            self.role = "student"
            self.location = None
    return MockUser()

@pytest.fixture
def controller(mock_user):
    mock_service = MagicMock()
    controller = UserController(user_service=mock_service)
    return controller

def test_get_users_returns_200(app, controller, mock_user):
    controller.is_session_valid = MagicMock(return_value=None)
    controller.user_service.get_users.return_value = [mock_user]

    with app.test_request_context():
        response = controller.get_users()
        assert response["code_status"] == 200
        assert "data" in response["response"].json

def test_get_specific_user_found(app, controller, mock_user):
    controller.is_session_valid = MagicMock(return_value=None)
    controller.user_service.get_specific_users.return_value = mock_user

    with app.test_request_context():
        response = controller.get_specific_users("1234")
        assert response["code_status"] == 200
        assert response["response"].json["data"]["email"] == "user.test@gmail.com"

def test_get_specific_user_not_found(app, controller):
    controller.is_session_valid = MagicMock(return_value=None)
    controller.user_service.get_specific_users.return_value = None

    with app.test_request_context():
        response = controller.get_specific_users("not-found-id")
        assert response["code_status"] == 404


def test_create_user_success(app, controller, mock_user):
    controller.user_service.create.return_value = mock_user
    controller.user_service.mail_exists.return_value = None
    controller._check_create_user_params = MagicMock(return_value=(True, "Ok"))

    request_data = {
        "name": "Test",
        "surname": "User",
        "password": "password",
        "email": "user.test@gmail.com",
        "status": "enabled",
        "role": "student"
    }

    client = app.test_client()
    response = client.post("/users", json=request_data)

    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["data"]["email"] == "user.test@gmail.com"

def test_create_user_conflict_email(app, controller):
    controller.user_service.mail_exists.return_value = True
    controller._check_create_user_params = MagicMock(return_value=(True, "Ok"))

    request_data = {
        "name": "Test",
        "surname": "User",
        "password": "password",
        "email": "user.test@gmail.com",
        "status": "enabled",
        "role": "student"
    }

    client = app.test_client()
    response = client.post("/users", json=request_data)

    assert response.status_code == 409


def test_login_user_success(app, controller, mock_user):
    controller.user_service.mail_exists.return_value = mock_user.uuid
    controller.user_service.get_specific_users.return_value = mock_user

    request_data = {
        "email": "user.test@gmail.com",
        "password": "password"
    }

    client = app.test_client()
    response = client.post("/users/login", json=request_data)

    assert response.status_code == 200
    response_data = response.get_json()
    assert response_data["data"]["email"] == "user.test@gmail.com"


def test_login_user_wrong_password(app, controller, mock_user):
    controller.user_service.mail_exists.return_value = mock_user.uuid
    mock_user.password = generate_password_hash("wrongpass")
    controller.user_service.get_specific_users.return_value = mock_user

    request_data = {
        "email": "user.test@gmail.com",
        "password": "invalid"
    }

    client = app.test_client()
    response = client.post("/users/login", json=request_data)

    assert response.status_code == 403


def test_delete_user_success(app, controller, mock_user):
    controller.get_specific_users = MagicMock(return_value={"code_status": 200})
    controller.user_service.delete = MagicMock()

    with app.test_request_context():
        response = controller.delete_specific_users("1234")
        assert response["code_status"] == 204

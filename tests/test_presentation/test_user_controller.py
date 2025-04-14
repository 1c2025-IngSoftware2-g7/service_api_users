import pytest
from unittest.mock import MagicMock, patch
from flask import Flask, jsonify
from presentation.user_controller import UserController
from werkzeug.security import generate_password_hash

@pytest.fixture
def app():
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.secret_key = "test"
    return app

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
    mock_logger = MagicMock()
    controller = UserController(user_service=mock_service, logger=mock_logger)
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

"""
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

    with app.test_request_context(json=request_data):
        request = app.test_client().post("/users", json=request_data)
        response = controller.create_users(request)
        assert response["code_status"] == 201
        assert response["response"].json["data"]["email"] == "user.test@gmail.com"

def test_create_user_conflict_email(app, controller):
    controller.user_service.mail_exists.return_value = True
    controller._check_create_user_params = MagicMock(return_value=(True, "Ok"))

    user_data = {
        "name": "Test",
        "surname": "User",
        "password": "password",
        "email": "user.test@gmail.com",
        "status": "enabled",
        "role": "student"
    }

    with app.test_request_context(json=user_data):
        request = app.test_client().post("/users", json=user_data)
        response = controller.create_users(request)
        assert response["code_status"] == 409

def test_login_user_success(app, controller, mock_user):
    controller.user_service.mail_exists.return_value = mock_user.uuid
    controller.user_service.get_specific_users.return_value = mock_user

    request_data = {
        "email": "user.test@gmail.com",
        "password": "password"
    }

    with app.test_request_context(json=request_data):
        with patch("application.user_controller.session", {}) as test_session:
            request = app.test_client().post("/users/login", json=request_data)
            response = controller.login_users(request)
            assert response["code_status"] == 200
            assert response["response"].json["data"]["email"] == "user.test@gmail.com"


def test_login_user_wrong_password(app, controller, mock_user):
    controller.user_service.mail_exists.return_value = mock_user.uuid
    mock_user.password = generate_password_hash("wrongpass")
    controller.user_service.get_specific_users.return_value = mock_user

    request_data = {
        "email": "user.test@gmail.com",
        "password": "invalid"
    }

    with app.test_request_context(json=request_data):
        request = app.test_client().post("/users/login", json=request_data)
        response = controller.login_users(request)
        assert response["code_status"] == 403
"""

def test_delete_user_success(app, controller, mock_user):
    controller.get_specific_users = MagicMock(return_value={"code_status": 200})
    controller.user_service.delete = MagicMock()

    with app.test_request_context():
        response = controller.delete_specific_users("1234")
        assert response["code_status"] == 204

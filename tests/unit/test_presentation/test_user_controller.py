import pytest
from unittest.mock import MagicMock
from werkzeug.security import generate_password_hash
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request as WerkzeugRequest
import uuid
from flask import Request, json

from presentation.user_controller import UserController
from headers import PUT_LOCATION

user_id = uuid.uuid4()

@pytest.fixture
def mock_user():
    class MockUser:
        def __init__(self):
            self.uuid = "1234"
            self.name = "Test"
            self.surname = "User"
            self.password = generate_password_hash("password")
            self.email = "user.test@gmail.com"
            self.status = "active"
            self.role = "student"
            self.location = None
            self.notification = True
            self.id_biometric = None
    return MockUser()

@pytest.fixture
def mock_request():
    return MagicMock()

@pytest.fixture
def controller(mock_user):
    mock_service = MagicMock()
    controller = UserController(user_service=mock_service)
    return controller

@pytest.fixture
def mock_error_json(monkeypatch):
    monkeypatch.setattr("presentation.user_controller.get_error_json", lambda *args, **kwargs: {"error": "mocked error"})

@pytest.fixture
def mock_controller():
    controller = UserController()
    controller.user_service = MagicMock()

    controller.user_service.mail_exists = MagicMock()
    controller.user_service.pin_in_progress = MagicMock()
    controller.user_service.pin_expired = MagicMock()
    controller.user_service.update_user = MagicMock()
    controller.user_service.create = MagicMock()

    controller._check_create_user_params = MagicMock(return_value=(True, ""))
    controller._serialize_user = MagicMock()

    return controller

@pytest.fixture
def request_factory():
    def _make_request(json_data):
        builder = EnvironBuilder(method="POST", path="/users", json=json_data)
        env = builder.get_environ()
        return Request(WerkzeugRequest(env))
    return _make_request

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


def test_create_user_success(controller, mock_user, mock_request):
    controller.user_service.create.return_value = mock_user
    controller.user_service.mail_exists.return_value = None
    controller._check_create_user_params = MagicMock(return_value=(True, "Ok"))

    mock_request.is_json = True
    mock_request.get_json.return_value = {
        "name": "Test",
        "surname": "User",
        "password": "password",
        "email": "user.test@gmail.com",
        "status": "active",
        "role": "student",
        "notification": True
    }

    result = controller.create_users(mock_request)

    assert result["code_status"] == 201
    assert result["response"].json["data"]["email"] == "user.test@gmail.com"

def test_create_user_conflict_409(mock_controller, request_factory):
    user_uuid = uuid.uuid4()

    request_data = {
        "email": "test@example.com",
        "password": "123456",
        "role": "user",
        "name": "Test",
        "surname": "User",
        "status": "active"
    }

    mock_controller.user_service.mail_exists.return_value = MagicMock(uuid=user_uuid)
    mock_controller.user_service.pin_in_progress.return_value = False
    mock_controller.user_service.pin_expired.return_value = False

    request = request_factory(request_data)
    response = mock_controller.create_users(request)

    assert response["code_status"] == 409

def test_create_user_pin_in_progress_307(controller, request_factory):
    user_uuid = uuid.uuid4()
    request_data = {
        "email": "test@example.com",
        "password": "123456",
        "role": "user"
    }

    controller.user_service.mail_exists.return_value = MagicMock(uuid=user_uuid)
    controller.pin_in_progress.return_value = True
    controller.pin_expired.return_value = False
    controller.user_service.update_user = MagicMock()
    controller._check_create_user_params.return_value = (True, "")
    request = request_factory(request_data)
    response = controller.create_users(request)

    assert response["code_status"] == 307
    controller.user_service.update_user.assert_called_once()


def test_create_user_pin_expired_201(controller, request_factory):
    user_uuid = uuid.uuid4()
    request_data = {"email": "test@example.com", "password": "123456", "role": "user"}
    updated_user = {"email": "test@example.com", "uuid": str(user_uuid)}

    controller.user_service.mail_exists.return_value = MagicMock(uuid=user_uuid)
    controller.pin_in_progress = MagicMock(return_value=False)
    controller.pin_expired = MagicMock(return_value=True)
    controller.user_service.update_user = MagicMock(return_value=updated_user)
    controller._serialize_user = MagicMock(return_value=updated_user)

    request = request_factory(request_data)
    response = controller.create_users(request)

    assert response["code_status"] == 201
    assert json.loads(response["response"].data)["data"]["email"] == "test@example.com"

def test_login_user_success(controller, mock_user, app):
    controller.user_service.mail_exists.return_value = mock_user
    controller.user_service.get_specific_users.return_value = mock_user

    mock_request = MagicMock()
    mock_request.is_json = True
    mock_request.get_json.return_value = {
        "email": "user.test@gmail.com",
        "password": "password"
    }

    with app.test_request_context():
        result = controller.login_users(mock_request)

    assert result["code_status"] == 200


def test_login_user_wrong_password(controller, mock_user):
    controller.user_service.mail_exists = MagicMock(return_value=mock_user)
    controller.user_service.get_specific_users = MagicMock(return_value=mock_user)

    mock_user.password = generate_password_hash("correctpassword")

    mock_request = MagicMock()
    mock_request.is_json = True
    mock_request.get_json.return_value = {
        "email": "user.test@gmail.com",
        "password": "wrongpassword"
    }

    response = controller.login_users(mock_request)

    assert response["code_status"] == 403


def test_delete_user_success(app, controller, mock_user):
    controller.get_specific_users = MagicMock(return_value={"code_status": 200})
    controller.user_service.delete = MagicMock()

    with app.test_request_context():
        response = controller.delete_specific_users("1234")
        assert response["code_status"] == 204


def test_get_active_teachers_returns_serialized_list(app, controller):
    mock_service = MagicMock()
    mock_teacher1 = MagicMock()
    mock_teacher2 = MagicMock()
    mock_service.get_active_teachers.return_value = [mock_teacher1, mock_teacher2]

    controller.user_service = mock_service
    controller._serialize_user = MagicMock(side_effect=[
        {"name": "Alice", "role": "teacher"},
        {"name": "Bob", "role": "teacher"},
    ])

    with app.test_request_context():
        result = controller.get_active_teachers()

    assert result["code_status"] == 200
    data = result["response"].get_json()
    assert data == {
        "data": [
            {"name": "Alice", "role": "teacher"},
            {"name": "Bob", "role": "teacher"}
        ]
    }

    mock_service.get_active_teachers.assert_called_once()
    assert controller._serialize_user.call_count == 2


def test_missing_required_fields(controller, mock_request):
    mock_request.get_json.return_value = {
        "admin_email": "admin@example.com"
    }

    response = controller.admin_change_user_status(mock_request)
    
    assert response["code_status"] == 400

def test_admin_authentication_failed(controller, mock_request):
    mock_request.get_json.return_value = {
        "admin_email": "admin@example.com",
        "admin_password": "wrongpass",
        "uuid": "user-uuid"
    }

    fake_admin = MagicMock()
    fake_admin.password = "correctpass"
    fake_admin.role = "student"

    controller.user_service.mail_exists.return_value = fake_admin

    response = controller.admin_change_user_status(mock_request)

    assert response["code_status"] == 403

def test_user_not_found(controller, mock_request):
    mock_request.get_json.return_value = {
        "admin_email": "admin@example.com",
        "admin_password": "adminpass",
        "uuid": "non-existent-uuid"
    }

    admin = MagicMock()
    admin.password = "adminpass"
    admin.role = "admin"

    controller.user_service.mail_exists.return_value = admin
    controller.user_service.get_specific_users.return_value = None

    response = controller.admin_change_user_status(mock_request)

    assert response["code_status"] == 400

def test_change_status_from_active_to_inactive(controller, mock_request):
    mock_request.get_json.return_value = {
        "admin_email": "admin@example.com",
        "admin_password": "adminpass",
        "uuid": "some-uuid"
    }

    admin = MagicMock()
    admin.password = "adminpass"
    admin.role = "admin"

    user = MagicMock()
    user.status = "active"

    controller.user_service.mail_exists.return_value = admin
    controller.user_service.get_specific_users.return_value = user

    response = controller.admin_change_user_status(mock_request)

    assert response["code_status"] == 201
    assert "inactive" in response["response"].json["message"]

def test_change_status_from_inactive_to_active(controller, mock_request):
    mock_request.get_json.return_value = {
        "admin_email": "admin@example.com",
        "admin_password": "adminpass",
        "uuid": "some-uuid"
    }

    admin = MagicMock()
    admin.password = "adminpass"
    admin.role = "admin"

    user = MagicMock()
    user.status = "inactive"

    controller.user_service.mail_exists.return_value = admin
    controller.user_service.get_specific_users.return_value = user

    response = controller.admin_change_user_status(mock_request)

    assert response["code_status"] == 201
    assert "active" in response["response"].json["message"]

def test_update_status_raises_exception(controller, mock_request):
    mock_request.get_json.return_value = {
        "admin_email": "admin@example.com",
        "admin_password": "adminpass",
        "uuid": "some-uuid"
    }

    admin = MagicMock()
    admin.password = "adminpass"
    admin.role = "admin"

    user = MagicMock()
    user.status = "active"

    controller.user_service.mail_exists.return_value = admin
    controller.user_service.get_specific_users.return_value = user
    controller.user_service.update_status.side_effect = Exception("DB error")

    response = controller.admin_change_user_status(mock_request)

    assert response["code_status"] == 500    

def test_initiate_password_recovery_success(controller):
    controller.user_service.initiate_password_recovery.return_value = {"message": "Recovery email sent", "code": 200}
    
    result = controller.initiate_password_recovery("test@example.com")
    
    assert result["code_status"] == 200
    assert result["response"].json["message"] == "Recovery email sent"

def test_initiate_password_recovery_exception(controller, mock_error_json):
    controller.user_service.initiate_password_recovery.side_effect = Exception("fail")
    
    result = controller.initiate_password_recovery("test@example.com")
    
    assert result["code_status"] == 500
    assert "mocked error" in result["response"]["error"]


def test_validate_recovery_pin_success_message(controller):
    controller.user_service.validate_recovery_pin.return_value = {"message": "PIN valid", "code": 200}
    
    result = controller.validate_recovery_pin("test@example.com", "1234")
    
    assert result["code_status"] == 200
    assert result["response"].json["message"] == "PIN valid"

def test_validate_recovery_pin_success_error(controller):
    controller.user_service.validate_recovery_pin.return_value = {"error": "Invalid PIN", "code": 400}
    
    result = controller.validate_recovery_pin("test@example.com", "wrongpin")
    
    assert result["code_status"] == 400
    assert result["response"].json["error"] == "Invalid PIN"

def test_validate_recovery_pin_exception(controller, mock_error_json):
    controller.user_service.validate_recovery_pin.side_effect = Exception("fail")
    
    result = controller.validate_recovery_pin("test@example.com", "1234")
    
    assert result["code_status"] == 500
    assert "mocked error" in result["response"]["error"]


def test_update_password_success_message(controller):
    controller.user_service.update_password.return_value = {"message": "Password updated", "code": 200}
    
    result = controller.update_password("test@example.com", "newpass")
    
    assert result["code_status"] == 200
    assert result["response"].json["message"] == "Password updated"

def test_update_password_success_error(controller):
    controller.user_service.update_password.return_value = {"error": "Update failed", "code": 400}
    
    result = controller.update_password("test@example.com", "newpass")
    
    assert result["code_status"] == 400
    assert result["response"].json["error"] == "Update failed"

def test_update_password_exception(controller, mock_error_json):
    controller.user_service.update_password.side_effect = Exception("fail")
    
    result = controller.update_password("test@example.com", "newpass")
    
    assert result["code_status"] == 500
    assert "mocked error" in result["response"]["error"]


def test_initiate_registration_confirmation_success(controller):
    controller.user_service.initiate_registration_confirmation.return_value = {"message": "Confirmation sent", "code": 200}
    
    result = controller.initiate_registration_confirmation("test@example.com")
    
    assert result["code_status"] == 200
    assert result["response"].json["message"] == "Confirmation sent"

def test_initiate_registration_confirmation_exception(controller, mock_error_json):
    controller.user_service.initiate_registration_confirmation.side_effect = Exception("fail")
    
    result = controller.initiate_registration_confirmation("test@example.com")
    
    assert result["code_status"] == 500
    assert "mocked error" in result["response"]["error"]


def test_validate_registration_pin_success_message(controller, mock_user):
    controller.user_service.validate_registration_pin.return_value = {"message": "PIN valid", "code": 200, "user": mock_user}
    
    result = controller.validate_registration_pin("test@example.com", "1234")
    
    assert result["code_status"] == 200
    assert result["response"].json["message"] == "PIN valid"

def test_validate_registration_pin_success_error(controller):
    controller.user_service.validate_registration_pin.return_value = {"error": "Invalid PIN", "code": 400}
    
    result = controller.validate_registration_pin("test@example.com", "wrongpin")
    
    assert result["code_status"] == 400
    assert result["response"].json["error"] == "Invalid PIN"

def test_validate_registration_pin_exception(controller, mock_error_json):
    controller.user_service.validate_registration_pin.side_effect = Exception("fail")
    
    result = controller.validate_registration_pin("test@example.com", "1234")
    
    assert result["code_status"] == 500
    assert "mocked error" in result["response"]["error"]


def test_set_location_missing_data(controller):
    request = MagicMock()
    request.get_json.return_value = {"latitude": None, "longitude": None}

    response = controller.set_user_location(user_id, request)

    assert response["code_status"] == 400
    assert "Location is required" in response["response"].get_json()["detail"]


def test_set_location_invalid_latitude(controller):
    request = MagicMock()
    request.get_json.return_value = {"latitude": "999", "longitude": "0"}

    response = controller.set_user_location(user_id, request)

    assert response["code_status"] == 400
    assert "Invalid latitude" in response["response"].get_json()["detail"]


def test_set_location_invalid_longitude(controller):
    request = MagicMock()
    request.get_json.return_value = {"latitude": "0", "longitude": "-999"}

    response = controller.set_user_location(user_id, request)

    assert response["code_status"] == 400
    assert "Invalid longitude" in response["response"].get_json()["detail"]


def test_set_location_user_not_found(controller):
    # valid location
    request = MagicMock()
    request.get_json.return_value = {"latitude": "45.0", "longitude": "60.0"}

    # User that not exist
    controller.get_specific_users = MagicMock(return_value={"code_status": 404})

    response = controller.set_user_location(user_id, request)

    assert response["code_status"] == 404
    assert "was not found" in response["response"].get_json()["detail"]


def test_set_location_success(controller):
    request = MagicMock()
    request.get_json.return_value = {"latitude": "45.0", "longitude": "60.0"}

    controller.get_specific_users = MagicMock(return_value={"code_status": 200})
    controller.user_service.set_location = MagicMock()

    response = controller.set_user_location(user_id, request)

    assert response["code_status"] == 200
    assert response["response"].get_json()["result"] == PUT_LOCATION

def test_create_admin_not_json(controller):
    request = MagicMock()
    request.is_json = False

    response = controller.create_admin_user(request)

    assert response["code_status"] == 400
    assert "is not json" in response["response"].get_json()["detail"]


def test_create_admin_missing_fields(controller):
    request = MagicMock()
    request.is_json = True
    request.get_json.return_value = {"admin_email": "admin@test.com"}

    response = controller.create_admin_user(request)

    assert response["code_status"] == 400
    assert "Missing fields" in response["response"].get_json()["detail"]


def test_create_admin_invalid_auth(controller):
    request = MagicMock()
    request.is_json = True
    request.get_json.return_value = {
        "admin_email": "admin@test.com",
        "admin_password": "1234",
        "name": "New",
        "surname": "Admin",
        "email": "new@admin.com",
        "password": "pass",
        "notification": True
    }

    controller.user_service.mail_exists.return_value = None

    response = controller.create_admin_user(request)

    assert response["code_status"] == 403
    assert "not admin or not check password hash" in response["response"].get_json()["detail"]


def test_create_admin_not_admin_role(controller):
    request = MagicMock()
    request.is_json = True
    request.get_json.return_value = {
        "admin_email": "admin@test.com",
        "admin_password": "1234",
        "name": "New",
        "surname": "Admin",
        "email": "new@admin.com",
        "password": "pass",
        "notification": True
    }

    fake_admin = MagicMock()
    fake_admin.password = "1234"
    fake_admin.role = "student"

    controller.user_service.mail_exists.return_value = fake_admin

    response = controller.create_admin_user(request)

    assert response["code_status"] == 403
    assert "is not admin" in response["response"].get_json()["detail"]


def test_create_admin_invalid_params(controller):
    request = MagicMock()
    request.is_json = True
    request.get_json.return_value = {
        "admin_email": "admin@test.com",
        "admin_password": "1234",
        "name": "New",
        "surname": "Admin",
        "email": "new@admin.com",
        "password": "pass",
        "notification": True
    }

    fake_admin = MagicMock()
    fake_admin.password = "1234"
    fake_admin.role = "admin"

    controller.user_service.mail_exists = MagicMock(return_value=fake_admin)
    controller._check_create_user_params = MagicMock(return_value=(False, "Invalid email"))
    controller.user_service.create = MagicMock()

    response = controller.create_admin_user(request)

    assert response["code_status"] == 400
    assert "Invalid email" in response["response"].get_json()["detail"]

def test_create_admin_create_fails(controller):
    request = MagicMock()
    request.is_json = True
    request.get_json.return_value = {
        "admin_email": "admin@test.com",
        "admin_password": "1234",
        "name": "New",
        "surname": "Admin",
        "email": "new@admin.com",
        "password": "pass",
        "notification": True
    }

    fake_admin = MagicMock()
    fake_admin.password = "1234"
    fake_admin.role = "admin"

    controller.user_service.mail_exists = MagicMock(return_value=fake_admin)
    controller._check_create_user_params = MagicMock(return_value=(True, "Ok"))
    controller.user_service.create = MagicMock(side_effect=Exception("DB error"))

    response = controller.create_admin_user(request)

    assert response["code_status"] == 500
    assert "DB error" in response["response"].get_json()["detail"]

def test_create_admin_success(controller):
    request = MagicMock()
    request.is_json = True
    request.get_json.return_value = {
        "admin_email": "admin@test.com",
        "admin_password": "1234",
        "name": "New",
        "surname": "Admin",
        "email": "new@admin.com",
        "password": "pass",
        "notification": True
    }

    fake_admin = MagicMock()
    fake_admin.password = "1234"
    fake_admin.role = "admin"

    controller.user_service.mail_exists = MagicMock(return_value=fake_admin)
    controller._check_create_user_params = MagicMock(return_value=(True, "Ok"))
    controller.user_service.create = MagicMock(return_value=True)

    response = controller.create_admin_user(request)

    assert response["code_status"] == 201
    assert response["response"].get_json()["message"] == "Admin user created successfully"

def test_login_admin_success(app, controller):
    with app.test_request_context():
        request = MagicMock()
        login_response = {
            "code_status": 200,
            "response": MagicMock()
        }
        login_response["response"].get_json.return_value = {
            "data": {
                "role": "admin",
                "name": "Admin"
            }
        }

        controller.login_users = MagicMock(return_value=login_response)

        response = controller.login_admin(request)

        assert response["code_status"] == 200
        assert response["response"].get_json()["message"] == "Admin login successful"

def test_login_admin_not_admin(controller):
    request = MagicMock()
    login_response = {
        "code_status": 200,
        "response": MagicMock()
    }
    login_response["response"].get_json.return_value = {
        "data": {
            "role": "student"  #no admin
        }
    }

    controller.login_users = MagicMock(return_value=login_response)

    response = controller.login_admin(request)

    assert response["code_status"] == 403
    assert "is not 'admin'" in response["response"].get_json()["detail"]

def test_login_admin_failed(controller):
    request = MagicMock()
    login_response = {
        "code_status": 403,
        "response": MagicMock()
    }

    controller.login_users = MagicMock(return_value=login_response)

    response = controller.login_admin(request)

    assert response["code_status"] == 403


def test_update_notification_success(controller, mock_user):
    mock_request = MagicMock()
    mock_request.is_json = True
    mock_request.get_json.return_value = {"notification": False}

    controller.user_service.update_notification.return_value = str(
        mock_user.uuid)
    controller.user_service.get_specific_users.return_value = mock_user

    response = controller.update_notification(mock_user.uuid, mock_request)

    assert response["code_status"] == 200
    assert response["response"].json["data"]["uuid"] == str(mock_user.uuid)


def test_login_biometric_success(controller, mock_user, app):
    mock_user.status = "active"
    mock_user.id_biometric = "bio123"
    controller.user_service.mail_exists.return_value = mock_user

    mock_request = MagicMock()
    mock_request.is_json = True
    mock_request.get_json.return_value = {
        "email": "user@test.com",
        "id_biometric": "bio123"
    }

    with app.test_request_context():
        response = controller.login_biometric(mock_request)

    assert response["code_status"] == 200
    assert "Biometric login successful" in response["response"].json["message"]


def test_update_biometric_id_invalid_request(controller):
    mock_request = MagicMock()
    mock_request.is_json = False

    response = controller.update_biometric_id("user123", mock_request)

    assert response["code_status"] == 400

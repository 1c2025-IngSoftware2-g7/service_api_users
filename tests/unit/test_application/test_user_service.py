import pytest
from unittest.mock import MagicMock

from application.user_service import UserService


@pytest.fixture
def user_service():
    mock_repo = MagicMock()
    mock_google = MagicMock()
    mock_email = MagicMock()
    service = UserService(mock_repo, mock_google, mock_email)
    return service, mock_repo, mock_google, mock_email


def test_get_users(user_service):
    service, repo, *_ = user_service
    repo.get_all_users.return_value = ["user1", "user2"]

    result = service.get_users()

    assert result == ["user1", "user2"]
    repo.get_all_users.assert_called_once()


def test_get_specific_users(user_service):
    service, repo, *_ = user_service
    repo.get_user.return_value = {"uuid": "123"}

    result = service.get_specific_users("123")

    assert result["uuid"] == "123"
    repo.get_user.assert_called_once_with("123")


def test_delete(user_service):
    service, repo, *_ = user_service

    service.delete("abc-123")

    repo.delete_users.assert_called_once_with("abc-123")


def test_create(user_service):
    service, repo, *_ = user_service
    mock_request = {"email": "test@example.com"}
    repo.get_user_with_email.return_value = {"email": "test@example.com"}

    result = service.create(mock_request)

    repo.insert_user.assert_called_once_with(mock_request)
    repo.get_user_with_email.assert_called_once_with("test@example.com")
    assert result["email"] == "test@example.com"


def test_set_location(user_service):
    service, repo, *_ = user_service

    service.set_location("uuid123", 12.34, 56.78)

    repo.set_location.assert_called_once_with({
        "uuid": "uuid123", "latitude": 12.34, "longitude": 56.78
    })


def test_mail_exists(user_service):
    service, repo, *_ = user_service
    repo.get_user_with_email.return_value = True

    result = service.mail_exists("mail@test.com")

    assert result is True
    repo.get_user_with_email.assert_called_once_with("mail@test.com")


def test_login_user_with_google(user_service):
    service, _, google, _ = user_service
    google.authorize_redirect.return_value = "redirect_url"

    result = service.login_user_with_google("admin")

    assert result == "redirect_url"


def test_authorize(user_service):
    service, _, google, _ = user_service
    google.authorize_access_token.return_value = "token"
    google.get_user_info.return_value = {"email": "test@test.com"}

    result = service.authorize()

    assert result["email"] == "test@test.com"
    google.authorize_access_token.assert_called_once()
    google.get_user_info.assert_called_once()


def test_create_users_if_not_exist_user_exists(user_service):
    service, repo, *_ = user_service
    repo.get_user_with_email.return_value = {"email": "test@test.com"}

    result = service.create_users_if_not_exist({"email": "test@test.com"})

    assert result["email"] == "test@test.com"
    repo.insert_user.assert_not_called()


def test_create_users_if_not_exist_user_not_exists(user_service):
    service, repo, *_ = user_service
    repo.get_user_with_email.side_effect = [None, {"email": "test@test.com"}]

    result = service.create_users_if_not_exist({"email": "test@test.com"})

    assert result["email"] == "test@test.com"
    repo.insert_user.assert_called_once()


def test_verify_user_existence(user_service):
    service, repo, *_ = user_service
    repo.get_user_with_email.return_value = {"email": "test@test.com"}

    result = service.verify_user_existence({"email": "test@test.com"})

    assert result["email"] == "test@test.com"
    repo.get_user_with_email.assert_called_once()


def test_create_users_already_exists(user_service):
    service, repo, *_ = user_service
    repo.get_user_with_email.return_value = {"email": "test@test.com"}

    result = service.create_users({"email": "test@test.com"})

    assert result["email"] == "test@test.com"
    repo.insert_user.assert_not_called()


def test_create_users_not_exists(user_service):
    service, repo, *_ = user_service
    repo.get_user_with_email.side_effect = [None, {"email": "test@test.com"}]

    result = service.create_users({"email": "test@test.com"})

    assert result["email"] == "test@test.com"
    repo.insert_user.assert_called_once()


def test_verify_google_token(user_service):
    service, _, google, _ = user_service
    google.verify_google_token.return_value = {"valid": True}

    result = service.verify_google_token("sometoken")

    assert result == {"valid": True}
    google.verify_google_token.assert_called_once_with("sometoken")


def test_initiate_password_recovery_success(user_service):
    service, repo, _, email = user_service
    user = MagicMock()
    user.uuid = "user-uuid"
    repo.get_user_with_email.return_value = user
    repo.get_active_pin.return_value = None
    email.send_pin_email.return_value = True

    response = service.initiate_password_recovery("test@example.com")

    assert response["code"] == 200
    repo.create_pin.assert_called_once()
    email.send_pin_email.assert_called_once()


def test_initiate_password_recovery_user_not_found(user_service):
    service, repo, _, _ = user_service
    repo.get_user_with_email.return_value = None

    response = service.initiate_password_recovery("missing@example.com")

    assert response["code"] == 404


def test_initiate_password_recovery_existing_pin(user_service):
    service, repo, *_= user_service
    user = MagicMock()
    user.uuid = "user-uuid"
    repo.get_user_with_email.return_value = user
    repo.get_active_pin.return_value = "some_pin"

    response = service.initiate_password_recovery("test@example.com")

    assert response["code"] == 429


def test_initiate_password_recovery_email_failure(user_service):
    service, repo, _, email = user_service
    user = MagicMock()
    user.uuid = "user-uuid"
    repo.get_user_with_email.return_value = user
    repo.get_active_pin.return_value = None
    email.send_pin_email.return_value = False

    response = service.initiate_password_recovery("test@example.com")

    assert response["code"] == 500

def test_get_active_teachers_returns_users(user_service):
    service, repo, *_= user_service
    expected_teachers = {
        "response": {"data": [
            {"email": "teacher1@example.com", "role": "teacher", "status": "active"},
            {"email": "teacher2@example.com", "role": "teacher", "status": "active"},
        ]},
        "code_status": 200
    }
    repo.get_active_teachers.return_value = expected_teachers

    result = service.get_active_teachers()

    assert result == expected_teachers
    repo.get_active_teachers.assert_called_once()

def test_validate_recovery_pin_valid(user_service):
    service, repo, *_= user_service
    repo.get_user_with_email.return_value = {"email": "test@example.com"}
    repo.validate_and_use_pin.return_value = True

    result = service.validate_recovery_pin("test@example.com", "1234")

    assert result["code"] == 200
    assert "PIN validated" in result["message"]

def test_validate_recovery_pin_invalid_pin(user_service):
    service, repo, *_= user_service
    repo.get_user_with_email.return_value = {"email": "test@example.com"}
    repo.validate_and_use_pin.return_value = False

    result = service.validate_recovery_pin("test@example.com", "wrongpin")

    assert result["code"] == 401
    assert "Invalid" in result["message"]

def test_validate_recovery_pin_missing_user(user_service):
    service, repo, *_= user_service
    repo.get_user_with_email.return_value = None

    result = service.validate_recovery_pin("nope@example.com", "1234")

    assert result["code"] == 404


def test_update_biometric_id_failure(user_service):
    service, repo, *_ = user_service
    repo.update_biometric_id.return_value = False

    result = service.update_biometric_id("user123", "new_bio_id")

    assert result is False


# def test_login_biometric_invalid_data(user_service):
#     service, *_ = user_service

#     result = service.login_biometric(None, None)
#     assert result["user"] is None
#     assert "required" in result["message"]

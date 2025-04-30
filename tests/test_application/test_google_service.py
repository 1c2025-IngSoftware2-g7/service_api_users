import pytest
import os
from unittest.mock import MagicMock, patch
from application.google_service import GoogleService


@pytest.fixture
def mock_oauth():
    return MagicMock()

@pytest.fixture
def google_service(mock_oauth):
    os.environ["GOOGLE_CLIENT_ID"] = "fake-client-id"
    os.environ["GOOGLE_CLIENT_SECRET"] = "fake-secret"
    os.environ["OAUTH_REDIRECT_URI"] = "http://localhost/oauth2callback"
    return GoogleService(mock_oauth)


def test_authorize_redirect(google_service):
    google_service.google.authorize_redirect.return_value = "redirect_url"

    result = google_service.authorize_redirect("student")

    google_service.google.authorize_redirect.assert_called_once_with(
        "http://localhost/oauth2callback", state="student"
    )
    assert result == "redirect_url"


def test_authorize_access_token(google_service):
    google_service.google.authorize_access_token.return_value = {"access_token": "abc123"}

    result = google_service.authorize_access_token()

    google_service.google.authorize_access_token.assert_called_once()
    assert result["access_token"] == "abc123"


def test_get_user_info(google_service):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "email": "test@example.com",
        "name": "Test User"
    }

    google_service.google.get.return_value = mock_response

    user_info = google_service.get_user_info()

    google_service.google.get.assert_called_once()
    assert user_info["email"] == "test@example.com"
    assert user_info["name"] == "Test User"


@patch("application.google_service.id_token.verify_oauth2_token")
@patch("application.google_service.requests.Request")
def test_verify_google_token_valid(mock_request, mock_verify, google_service):
    mock_verify.return_value = {
        "email": "test@gmail.com",
        "email_verified": True,
        "name": "Valid User",
        "picture": "http://image.url",
        "sub": "google-id-123"
    }

    token = "valid.token.value"
    result = google_service.verify_google_token(token)

    mock_verify.assert_called_once_with(token, mock_request(), audience="fake-client-id")
    assert result["email"] == "test@gmail.com"
    assert result["google_id"] == "google-id-123"


@patch("application.google_service.id_token.verify_oauth2_token")
@patch("application.google_service.requests.Request")
def test_verify_google_token_invalid_email(mock_request, mock_verify, google_service):
    mock_verify.return_value = {
        "email": "test@gmail.com",
        "email_verified": False
    }

    result = google_service.verify_google_token("invalid.token")
    assert result is None


@patch("application.google_service.id_token.verify_oauth2_token", side_effect=ValueError("Invalid Token"))
@patch("application.google_service.requests.Request")
def test_verify_google_token_raises_exception(mock_request, mock_verify, google_service):
    result = google_service.verify_google_token("broken.token")
    assert result is None

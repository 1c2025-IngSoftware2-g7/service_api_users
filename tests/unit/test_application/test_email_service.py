import pytest
from unittest.mock import patch, MagicMock
from application.email_service import EmailService


@pytest.fixture
def email_service():
    return EmailService()


@patch("application.email_service.current_app")
@patch("application.email_service.smtplib.SMTP")
def test_send_pin_email_success(mock_smtp, mock_current_app, email_service):
    # Mocks
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    # Call method
    result = email_service.send_pin_email(
        recipient_email="test@example.com",
        pin_code="123456",
        is_registration=True
    )

    # Assertions
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with(
        email_service.smtp_username,
        email_service.smtp_password
    )
    mock_server.send_message.assert_called_once()
    mock_current_app.logger.info.assert_called_once_with(
        "Email enviado a test@example.com"
    )
    assert result is True


@patch("application.email_service.current_app")
@patch("application.email_service.smtplib.SMTP", side_effect=Exception("SMTP error"))
def test_send_pin_email_failure(mock_smtp, mock_current_app, email_service):
    result = email_service.send_pin_email(
        recipient_email="fail@example.com",
        pin_code="654321",
        is_registration=False
    )

    mock_current_app.logger.error.assert_called_once()
    assert result is False

import smtplib
from email.mime.text import MIMEText
import os

from logger_config import get_logger

logger = get_logger("api-users")


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('EMAIL_FROM')
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

    def send_pin_email(self, recipient_email: str, pin_code: str, is_registration: bool):
        try:
            subject = "Verificación de registro" if is_registration else "Recuperación de contraseña"

            message = f"""
            Su código de verificación es: <strong>{pin_code}</strong>
            <p>{'Complete su registro' if is_registration else 'Ingrese este código para restablecer su contraseña'}</p>
            <p>El código expirará en 10 minutos.</p>
            """

            msg = MIMEText(message, 'html')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email enviado a {recipient_email}")
            return True
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return False

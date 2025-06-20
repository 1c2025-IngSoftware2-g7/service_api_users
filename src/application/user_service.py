import random
import string

from infrastructure.persistence.users_repository import UsersRepository
from application.email_service import EmailService
from logger_config import get_logger

logger = get_logger("api-users")

""" 
The application layer contains all the logic that is required by the application to meet its functional requirements and, 
at the same time, is not a part of the domain rules. In most systems that I've worked with, the application layer consisted 
of services orchestrating the domain objects to fulfill a use case scenario.

This layer can include:
- Service Application
- Use Case
- Interacting between domains
- Functions for each feature of our API using domain entities
- Entry points to the domain
- Communicates with the repository layer, which can return a User domain
"""


class UserService:
    def __init__(self, user_repository: UsersRepository, google, email_service):
        self.google = google
        self.user_repository = user_repository
        self.email_service = email_service

    def get_users(self):
        """Get all users."""
        users = self.user_repository.get_all_users()
        return users
    
    def get_active_teachers(self):
        """Get active teachers."""
        users = self.user_repository.get_active_teachers()
        return users

    def get_specific_users(self, uuid):
        """Get specific user."""
        user = self.user_repository.get_user(uuid)
        return user

    def delete(self, uuid):
        """Delete user."""
        self.user_repository.delete_users(uuid)
        return

    def create(self, request):
        """Create a users."""
        self.user_repository.insert_user(request)
        return self.user_repository.get_user_with_email(request["email"])

    def set_location(self, uuid, latitude, longitude):
        """Add location."""
        self.user_repository.set_location(
            {"uuid": uuid, "latitude": latitude, "longitude": longitude}
        )
        return

    def mail_exists(self, email):
        """  Function that check if a mail is valid on the database. If it is, we return the the user."""
        return self.user_repository.get_user_with_email(email)

    def login_user_with_google(self, role):
        """Login a user with google."""
        logger.info(f"In service - login_user_with_google - role: {role}")
        return self.google.authorize_redirect(role)

    def authorize(self):
        token = self.google.authorize_access_token()
        logger.info(f"In service - authorize - token: {token}")
        return self.google.get_user_info()

    def create_users_if_not_exist(self, user_info):
        user = self.user_repository.get_user_with_email(user_info["email"])
        logger.info(f"In service - create_users_if_not_exist - user: {user}")
        if user != None:
            return user

        logger.info(
            f"User does not exist. Create user with the following parameters: {user_info}"
        )

        self.user_repository.insert_user(user_info)
        user = self.user_repository.get_user_with_email(user_info["email"])
        return user

    def verify_user_existence(self, user_info):
        user = self.user_repository.get_user_with_email(user_info["email"])
        logger.info(f"In service - create_users_if_not_exist - user: {user}")
        return user

    def create_users(self, user_info):
        user = self.user_repository.get_user_with_email(user_info["email"])
        logger.info(f"In service - create_users - user: {user}")
        if user != None:
            return user

        logger.info(
            f"User does not exist. Create user with the following parameters: {user_info}"
        )

        self.user_repository.insert_user(user_info)
        user = self.user_repository.get_user_with_email(user_info["email"])
        return user

    def verify_google_token(self, token):
        return self.google.verify_google_token(token)

    def initiate_password_recovery(self, email):
        """Iniciar el proceso de recuperación de contraseña"""
        user = self.user_repository.get_user_with_email(email)
        if not user:
            return {"message": "No user found with this email", "code": 404}

        # Verificar si ya existe un PIN activo
        existing_pin = self.user_repository.get_active_pin(
            user.uuid, "password_recovery")
        if existing_pin:
            return {
                "message": "There's already an active PIN for this user. Please wait 10 minutes.",
                "code": 429
            }

        # Generar PIN de 6 dígitos
        pin_code = ''.join(random.choices(string.digits, k=4))

        # Guardar el PIN
        self.user_repository.create_pin(user.uuid, pin_code, "password_recovery")

        # En producción aquí iría el envío del email
        logger.info(f"PIN generado para {email}: {pin_code}")

        # Enviar email
        email_sent = self.email_service.send_pin_email(
            recipient_email=email,
            pin_code=pin_code,
            is_registration=False
        )

        if not email_sent:
            return {"message": "Failed to send email", "code": 500}

        return {
            "message": "Password recovery process initiated",
            "code": 200
        }

    def validate_recovery_pin(self, email: str, pin_code: str) -> dict:
        """Valida un PIN de recuperación de contraseña"""
        if not email or not pin_code:
            return {"message": "Email and PIN are required", "code": 400}

        user = self.user_repository.get_user_with_email(email)
        if not user:
            return {"message": "No user found with this email", "code": 404}


        is_valid = self.user_repository.validate_and_use_pin(
            email=email,
            pin_code=pin_code,
            pin_type="password_recovery"
        )

        if not is_valid:
            return {
                "message": "Invalid or expired PIN. Please generate a new one",
                "code": 401
            }

        return {"message": "PIN validated successfully", "code": 200}

    def update_password(self, email, new_password):
        """Actualiza la contraseña de un usuario"""
        if not email or not new_password:
            return {"message": "Email and new password are required", "code": 400}

        # Verificar que el usuario existe
        user = self.user_repository.get_user_with_email(email)
        if not user:
            return {"message": "No user found with this email", "code": 404}

        # Actualizar contraseña
        success = self.user_repository.update_user_password(email, new_password)
        if not success:
            return {"message": "Failed to update password", "code": 500}

        # Invalidar todos los PINs existentes
        self.user_repository.invalidate_all_pins(user.uuid)

        return {"message": "Password updated successfully", "code": 200}

    def initiate_registration_confirmation(self, email):
        """Iniciar el proceso de confirmación de registro"""
        user = self.user_repository.get_user_with_email(email)
        if not user:
            return {"message": "No user found with this email", "code": 404}

        # Verificar si ya existe un PIN activo
        existing_pin = self.user_repository.get_active_pin(
            user.uuid, "registration")
        if existing_pin:
            return {
                "message": "There's already an active registration PIN for this user. Please wait 10 minutes.",
                "code": 429
            }

        # Generar PIN de 6 dígitos
        pin_code = ''.join(random.choices(string.digits, k=4))

        # Guardar el PIN
        self.user_repository.create_pin(user.uuid, pin_code, "registration")

        # Enviar email
        email_sent = self.email_service.send_pin_email(
            recipient_email=email,
            pin_code=pin_code,
            is_registration=True
        )

        if not email_sent:
            return {"message": "Failed to send email", "code": 500}

        return {
            "message": "Registration confirmation PIN generated",
            "code": 200
        }

    def validate_registration_pin(self, email, pin_code):
        """Valida un PIN de confirmación de registro"""
        if not email or not pin_code:
            return {"message": "Email and PIN are required", "code": 400}

        # Verificar que el usuario existe
        user = self.user_repository.get_user_with_email(email)
        if not user:
            return {"message": "No user found with this email", "code": 404}

        # Validar el PIN
        is_valid = self.user_repository.validate_and_use_pin(
            email=email,
            pin_code=pin_code,
            pin_type="registration"
        )

        if not is_valid:
            return {
                "message": "Invalid or expired registration PIN. Please request a new one",
                "code": 401
            }

        self.user_repository.activate_user(email)

        return {"message": "Account verified successfully", "code": 200}

    def update_status(self, uuid, new_status):
        """
        Changes the status to the indicated one.
        If this is not possible, an error is generated.
        """
        result = self.user_repository.update_status(uuid, new_status)
        if not result:
            raise ValueError("Status could not be updated.")

    def update_notification(self, uuid, new_notification_status): 
        result = self.user_repository.update_notification(uuid, new_notification_status)
        if not result:
            raise ValueError("'notification' could not be updated.")
        return result

    def login_biometric(self, email: str, id_biometrico: str) -> dict:
        """
        Authenticate user using biometric data
        Returns:
            dict: {'user': User object if successful, None otherwise, 'message': str}
        """
        user = self.user_repository.get_user_with_email(email)

        if not user:
            return {'user': None, 'message': 'Usuario no encontrado'}

        if user.status == 'disabled':
            return {'user': None, 'message': 'Usuario bloqueado'}

        if user.id_biometrico != id_biometrico:
            return {'user': None, 'message': 'Autenticación biométrica fallida'}

        return {'user': user, 'message': 'Autenticación exitosa'}

from datetime import timedelta
import logging
import os
from flask import Flask, request, jsonify, g
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from app_factory import AppFactory


users_app = Flask(__name__)
CORS(
    users_app,
    origins=["*"],
    supports_credentials=True,
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS"],
)

users_app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_SAMESITE="None")


# Session config
users_app.secret_key = os.getenv("SECRET_KEY_SESSION")
users_app.permanent_session_lifetime = timedelta(minutes=5)

# OAuth config
oauth = OAuth(users_app)

# Logger config
env = os.getenv("FLASK_ENV")
log_level = logging.DEBUG if env == "development" else logging.INFO
users_app.logger.setLevel(log_level)

# Create layers
user_controller = AppFactory.create(oauth)

SWAGGER_URL = "/docs"
API_URL = "/static/openapi.yaml"
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL, API_URL, config={"app_name": "Users API"}
)
users_app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Endpoints:


@users_app.get("/health")
def health_check():
    return {"status": "ok"}, 200


@users_app.get("/users")
def get_users():
    """
    Get all users.
    """
    result = user_controller.get_users()

    return result["response"], result["code_status"]


@users_app.get("/users/<uuid:uuid>")
def get_specific_users(uuid):
    """
    Get specific user.
    """
    result = user_controller.get_specific_users(uuid)
    return result["response"], result["code_status"]


@users_app.delete("/users/<uuid:uuid>")
def delete_specific_users(uuid):
    """
    Delete user.
    """
    result = user_controller.delete_specific_users(uuid)
    return result["response"], result["code_status"]


@users_app.post("/users")
def add_users():
    """
    Create a users.
    In Flask: uuid.UUID is serialized to a string.
    """
    result = user_controller.create_users(request)
    return result["response"], result["code_status"]


@users_app.put("/users/<uuid:user_id>/location")
def set_user_location(user_id):
    """
    Add user location.
    """
    result = user_controller.set_user_location(user_id, request)
    return result["response"], result["code_status"]


@users_app.post("/users/login")
def login_users():
    """
    Login a user
    """
    result = user_controller.login_users(request)
    return result["response"], result["code_status"]


@users_app.post("/users/admin")
def add_admin():
    """
    Create an admin
    """
    result = user_controller.create_admin_user(request)
    return result["response"], result["code_status"]


@users_app.post("/users/admin/login")
def login_admin():
    """
    Login an admin.
    """
    result = user_controller.login_admin(request)
    return result["response"], result["code_status"]


@users_app.get("/users/login/google")
def login_user_with_google():
    """
    Login a user with google.

    "role" query param is needed.
    Default: student.
    Ex: '?role=student' or '?role=teacher'.
    """
    users_app.logger.info(f"Users API - In /users/login/google with request: {request}")
    return user_controller.login_user_with_google(request)


@users_app.get("/users/authorize")
def authorize():
    users_app.logger.debug(f"Users API - In GET /users/authorize with request: {request}")
    result = user_controller.authorize(request)
    return result["response"], result["code_status"]


@users_app.post("/users/authorize")
def authorize_with_token():
    """
    Authorize token with google.

    "role" query param is needed.
    Default: student.
    Ex: '?role=student' or '?role=teacher'.
    """
    users_app.logger.debug(f"Users API - In POST /users/authorize with request: {request}")
    result = user_controller.authorize_with_token(request)
    return result["response"], result["code_status"]


@users_app.post("/users/signup/google")
def post_signup_google():
    """
    User sign up.
    Body: token, role, email_verified, email, given_name, family_name, photo.

    Create profile: POST /profiles --> TODO: Move to API gateway.
    """
    users_app.logger.debug(f"Users API - In POST /users/signup/google with request: {request}")
    result = user_controller.authorize_signup_token(request)

    return result["response"], result["code_status"]


@users_app.post("/users/login/google")
def post_login_google():
    """
    User login.
    Body: token, email_verified, email, given_name, family_name, photo.
    If the status is "disabled" in db, user is not returned. User locked error is returned.

    UPDATE /profiles with photo --> TODO: Move to API gateway.
    """
    users_app.logger.debug(f"Users API - In POST /users/login/google with request: {request}")
    result = user_controller.authorize_login_token(request)
    return result["response"], result["code_status"]


@users_app.post("/users/<string:user_email>/password-recovery")
def password_recovery(user_email):
    """
    Iniciar proceso de recuperación de contraseña
    responses:
      200:description: PIN de recuperación generado exitosamente
      404:description: No existe usuario con ese email
      429:description: Ya existe un PIN activo para este usuario
    """
    result = user_controller.initiate_password_recovery(user_email)
    return result["response"], result["code_status"]


@users_app.put("/users/<string:user_email>/password-recovery")
def validate_recovery_pin(user_email):
    """
    Validar PIN de recuperación de contraseña
    responses:
      200: description: PIN validado correctamente
      400: description: Datos faltantes
      401: description: PIN inválido o expirado
    """
    data = request.get_json()
    if not data or "pin" not in data:
        return jsonify({"error": "Se requiere el campo 'pin'"}), 400

    pin_code = data["pin"]
    result = user_controller.validate_recovery_pin(user_email, pin_code)
    return result["response"], result["code_status"]


@users_app.put("/users/<string:user_email>/password")
def update_password(user_email):
    """
    Actualizar contraseña de usuario
    responses:
      200: description: Contraseña actualizada exitosamente
      400: description: Datos faltantes
      404: description: Usuario no encontrado
    """
    data = request.get_json()
    if not data or "new_password" not in data:
        return jsonify({"error": "Se requiere el campo 'new_password'"}), 400

    new_password = data["new_password"]
    result = user_controller.update_password(user_email, new_password)
    return result["response"], result["code_status"]


@users_app.post("/users/<string:user_email>/confirm-registration")
def registration_confirmation(user_email):
    """
    Iniciar proceso de confirmación de registro
    responses:
      200: description: PIN de confirmación generado
      404: description: Usuario no encontrado
      429: description: Ya existe un PIN activo
    """
    result = user_controller.initiate_registration_confirmation(user_email)
    return result["response"], result["code_status"]


@users_app.put("/users/<string:user_email>/confirm-registration")
def validate_registration_pin(user_email):
    """
    Validar PIN de confirmación de registro
    responses:
      200: description: Cuenta verificada exitosamente
      400: description: Datos faltantes
      401: description: PIN inválido o expirado
      404: description: Usuario no encontrado
    """
    data = request.get_json()
    if not data or "pin" not in data:
        return jsonify({"error": "Se requiere el campo 'pin'"}), 400

    pin_code = data["pin"]
    result = user_controller.validate_registration_pin(user_email, pin_code)
    return result["response"], result["code_status"]

from datetime import timedelta
import logging
import os
from flask import Flask, request, jsonify, g
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from app_factory import AppFactory
from logger_config import get_logger

users_app = Flask(__name__)
CORS(
    users_app,
    origins=["*"],
    supports_credentials=True,
    allow_headers=["Content-Type"],
    methods=["GET", "POST", "OPTIONS", "PUT"],
)

users_app.config.update(SESSION_COOKIE_SECURE=True, SESSION_COOKIE_SAMESITE="None")


# Session config
users_app.secret_key = os.getenv("SECRET_KEY_SESSION")
users_app.permanent_session_lifetime = timedelta(minutes=5)

# OAuth config
oauth = OAuth(users_app)

# Logger config
logger = get_logger("api-users")

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


@users_app.get("/users/admin")
def get_users():
    """
    Get all users.
    No session control.
    """
    result = user_controller.get_users_without_check_session()

    return result["response"], result["code_status"]


@users_app.get("/users/<uuid:uuid>")
def get_specific_users(uuid):
    """
    Get specific user.
    """
    result = user_controller.get_specific_users(uuid)
    return result["response"], result["code_status"]


@users_app.get("/users_check/<uuid:uuid>")
def get_specific_users_in_check(uuid):
    """
    Get specific user.
    Without session check.
    """
    result = user_controller.get_specific_users_in_check(uuid)
    return result["response"], result["code_status"]


@users_app.get("/users/teachers")
def get_active_teachers():
    """
    Get users with role=teacher and status=active.
    """
    result = user_controller.get_active_teachers()
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
    logger.info(f"In /users/login/google with request: {request}")
    return user_controller.login_user_with_google(request)


@users_app.get("/users/authorize")
def authorize():
    logger.debug(f"In GET /users/authorize with request: {request}")
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
    logger.debug(f"In POST /users/authorize with request: {request}")
    result = user_controller.authorize_with_token(request)
    return result["response"], result["code_status"]


@users_app.post("/users/signup/google")
def post_signup_google():
    """
    User sign up.
    Body: token, role, email_verified, email, given_name, family_name, photo.

    Create profile: POST /profiles --> TODO: Move to API gateway.
    """
    logger.debug(f"In POST /users/signup/google with request: {request}")
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
    logger.debug(f"In POST /users/login/google with request: {request}")
    result = user_controller.authorize_login_token(request)
    return result["response"], result["code_status"]


@users_app.post("/users/<string:user_email>/password-recovery")
def password_recovery(user_email):
    """
    Start password recovery process
    responses:
    200:description: Recovery PIN generated successfully
    404:description: No user with that email address
    429:description: An active PIN already exists for this user
    """
    result = user_controller.initiate_password_recovery(user_email)
    return result["response"], result["code_status"]


@users_app.put("/users/<string:user_email>/password-recovery")
def validate_recovery_pin(user_email):
    """
    Validate Password Recovery PIN
    Responses:
    200: Description: PIN validated successfully
    400: Description: Missing data
    401: Description: Invalid or expired PIN
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
    Update user password
    responses:
    200: description: Password updated successfully
    400: description: Missing data
    404: description: User not found
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
    Start registration confirmation process
    responses:
    200: description: Confirmation PIN generated
    404: description: User not found
    429: description: An active PIN already exists
    """
    result = user_controller.initiate_registration_confirmation(user_email)
    return result["response"], result["code_status"]


@users_app.put("/users/<string:user_email>/confirm-registration")
def validate_registration_pin(user_email):
    """
    Validate Registration Confirmation PIN
    Responses:
    200: Description: Account successfully verified
    400: Description: Missing data
    401: Description: Invalid or expired PIN
    S: Description: User not found
    """
    data = request.get_json()
    if not data or "pin" not in data:
        return jsonify({"error": "Se requiere el campo 'pin'"}), 400

    pin_code = data["pin"]
    result = user_controller.validate_registration_pin(user_email, pin_code)
    return result["response"], result["code_status"]


@users_app.put("/users/admin/status")
def admin_change_user_status():
    """
    Admin change user status.
    """
    result = user_controller.admin_change_user_status(request)
    return result["response"], result["code_status"]

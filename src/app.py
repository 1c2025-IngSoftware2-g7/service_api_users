from datetime import timedelta
import logging
import os
from flask import Flask, request
from authlib.integrations.flask_client import OAuth
from flask_cors import CORS

from src.app_factory import AppFactory


users_app = Flask(__name__)
CORS(users_app)

# Session config
users_app.secret_key = os.getenv("SECRET_KEY_SESSION")
users_app.permanent_session_lifetime = timedelta(minutes=5) 

# OAuth config
oauth = OAuth(users_app)

# Logger config
env = os.getenv("FLASK_ENV")
log_level = logging.DEBUG if env == "development" else logging.INFO
users_app.logger.setLevel(log_level)
users_logger = users_app.logger

# Create layers
user_controller = AppFactory.create(users_logger, oauth)


@users_app.get("/health")
def health_check():
    return {"status": "ok"}, 200


"""
Get all users.
"""
@users_app.get("/users")
def get_users():
    result = user_controller.get_users()

    return result["response"], result["code_status"]


"""
Get specific user.
"""
@users_app.get("/users/<uuid:uuid>")
def get_specific_users(uuid):
    result = user_controller.get_specific_users(uuid)
    return result["response"], result["code_status"]


"""
Delete user.
"""
@users_app.delete("/users/<uuid:uuid>")
def delete_specific_users(uuid):
    result = user_controller.delete_specific_users(uuid)
    return result["response"], result["code_status"]


"""
Create a users.
In Flask: uuid.UUID is serialized to a string.
"""
@users_app.post("/users")
def add_users():
    result = user_controller.create_users(request)
    return result["response"], result["code_status"]


"""
Add user location.
"""
@users_app.put("/users/<uuid:user_id>/location")
def set_user_location(user_id):
    result = user_controller.set_user_location(user_id, request)
    return result["response"], result["code_status"]


"""
Login a user
"""
@users_app.post("/users/login")
def login_users():
    result = user_controller.login_users(request)
    return result["response"], result["code_status"]


"""
Create an admin
"""
@users_app.post("/users/admin")
def add_admin():
    result = user_controller.create_admin_user(request)
    return result["response"], result["code_status"]


"""
Login an admin.
"""
@users_app.post("/users/admin/login")
def login_admin():
    result = user_controller.login_admin(request)
    return result["response"], result["code_status"]


"""
Login a user with google.

"role" query param is needed. 
Default: student.
Ex: '?role=student' or '?role=teacher'.
"""
@users_app.get("/users/login/google")
def login_user_with_google():
    return user_controller.login_user_with_google(request)


@users_app.get('/users/authorize')
def authorize():
    result = user_controller.authorize(request)
    return result["response"], result["code_status"]

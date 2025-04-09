import logging
import os
from flask import Flask, request

from app_factory import AppFactory

users_app = Flask(__name__)
env = os.getenv("FLASK_ENV")
log_level = logging.DEBUG if env == "development" else logging.INFO
users_app.logger.setLevel(log_level)
users_logger = users_app.logger

user_controller = AppFactory.create(users_logger)


@users_app.before_request
def skip_auth_for_testing():
    if os.getenv("FLASK_ENV") == "testing":
        return  # Skip auth in testing environment
    
    # Auth logic would go here


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
Login de administrador.
"""
@users_app.post("/users/admin/login")
def login_admin():
    result = user_controller.login_admin(request)
    return result["response"], result["code_status"]

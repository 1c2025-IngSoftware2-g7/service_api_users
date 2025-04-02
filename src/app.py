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

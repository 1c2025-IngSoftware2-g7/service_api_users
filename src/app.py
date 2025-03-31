import logging
import os
from flask import Flask, request

from src.application.user_service import UserService
from src.infrastructure.persistence.users_repository import UsersRepository
from src.presentation.user_controller import UserController

users_app = Flask(__name__)

env = os.getenv("FLASK_ENV")

log_level = logging.DEBUG if env == "development" else logging.INFO
users_app.logger.setLevel(log_level)
users_logger = users_app.logger

# Here: - Each class is created: presentation, infrastructure, controller.

"""
Get all users.
"""
@users_app.get("/users")
def get_users():
    user_repository = UsersRepository()
    user_service = UserService(user_repository)
    user_controller = UserController(user_service)
    result = user_controller.get_users()

    return result["response"], result["code_status"] #jsonify({"data": users}), 200


"""
Get specific user.
"""
@users_app.get("/users/<uuid:uuid>")
def get_specific_users(uuid):
    user_repository = UsersRepository()
    user_service = UserService(user_repository)
    user_controller = UserController(user_service)
    result = user_controller.get_user(uuid)

    return result["response"], result["code_status"]


"""
Delete user.
"""
@users_app.delete("/users/<uuid:uuid>")
def delete_specific_users(uuid):
    user_repository = UsersRepository()
    user_service = UserService(user_repository)
    user_controller = UserController(user_service)

    result = user_controller.delete(uuid)
    return result["response"], result["code_status"]


"""
Create a users.
In Flask: uuid.UUID is serialized to a string.
"""
@users_app.post("/users")
def add_users():
    user_repository = UsersRepository()
    user_service = UserService(user_repository)
    user_controller = UserController(user_service)

    result = user_controller.create_user(request)
    return result["response"], result["code_status"]

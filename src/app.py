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
Login a user with google
"""
@users_app.post("/users/login/google")
def login_user_with_google():
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@users_app.route('/authorize')
def authorize():
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    
    # Aquí buscás al usuario en tu DB por email o lo creás si no existe
    user_email = user_info['email']
    
    # Guardás en sesión
    session['user'] = user_info
    return jsonify(user_info)

from flask import Flask, request, jsonify
import uuid
import logging
import os

from headers import BAD_REQUEST, DELETE, NOT_users

users_app = Flask(__name__)

env = os.getenv("FLASK_ENV")

log_level = logging.DEBUG if env == "development" else logging.INFO
users_app.logger.setLevel(log_level)

users_logger = users_app.logger

"""
Get all users.
"""
@users_app.get("/users")
def get_users():
    # execute_query
    users = []

    return jsonify({"data": users}), 200


"""
Get specific user.
"""
@users_app.get("/users/<uuid:uuid>")
def get_specific_users(uuid):
    # execute_query {"uuid": uuid}
    user = {}

    if user:
        return jsonify({"data": user}), 200

    users_logger.error(f"{NOT_users} with uuid {uuid}")
    return (
        jsonify(
            {
                "type": "about:blank",
                "title": NOT_users,
                "status": 0,
                "detail": f"The users with uuid {uuid} was not found",
                "instance": f"/users/{uuid}",
            }
        ),
        404,
    )


"""
Delete user.
"""
@users_app.delete("/users/<uuid:uuid>")
def delete_specific_users(uuid):
    # SELECT execute_query {"uuid": uuid}
    user = {}

    if user:
        # DELETE execute_query {"uuid": uuid}
        return jsonify({"result": DELETE}), 204

    users_logger.error(f"{NOT_users} with uuid {uuid}")
    return (
        jsonify(
            {
                "type": "about:blank",
                "title": NOT_users,
                "status": 0,
                "detail": f"The users with uuid {uuid} was not found",
                "instance": f"/users/{uuid}",
            }
        ),
        404,
    )


"""
Create a users.
In Flask: uuid.UUID is serialized to a string.
"""
@users_app.post("/users")
def add_users():
    if request.is_json:
        users = request.get_json()
        # INSERT execute_query users
        return jsonify({"data": users}), 201

    users_logger.error(f"{BAD_REQUEST} with body: {users}")
    return (
        jsonify(
            {
                "type": "about:blank",
                "title": BAD_REQUEST,
                "status": 0,
                "detail": f"{BAD_REQUEST} with body: {users}",
                "instance": f"/users",
            }
        ),
        400,
    )

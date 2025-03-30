from flask import jsonify

from headers import BAD_REQUEST, DELETE, NOT_USER
from src.application.user_service import UserService
from src.infrastructure.persistence.users_repository import UsersRepository

""" 
The presentation layer contains all of the classes responsible for presenting the UI to the end-user 
or sending the response back to the client (in case we’re operating deep in the back-end).

- It has serialization and deserialization logic. Validations. Authentication.
"""
class UserController:
    def __init___(self, user_service: UserService): 
        # Layered Architecture: Each class receives the instance of the other classes.
        self.user_service = user_service
        return        

    """Get all users."""
    def get_users(self):
        users = self.user_servide.get_users() # list of instance of Users() (domain)
        
        # deserialize users:
        return {
            "response": jsonify({"data": users}), 
            "code_status": 200
        }
        
    """
    Get specific user.
    """
    def get_specific_users(self, uuid):
        user = self.user_servide.get_specific_users(uuid) # instance of Users() (domain)

        if user:
            return jsonify({"data": user}), 200
        
        return {
            "response": jsonify(
                {
                    "type": "about:blank",
                    "title": NOT_USER,
                    "status": 0,
                    "detail": f"The users with uuid {uuid} was not found",
                    "instance": f"/users/{uuid}",
                }
            ),
            "code_status": 404,
        }


    """
    Delete user.
    """
    def delete_specific_users(self, uuid):
        if self.get_user(uuid):
            self.user_service.delete(uuid)
            return {
                "response": jsonify({"result": DELETE}), 
                "code_status": 204
            }

        return {
            "response": jsonify(
                {
                    "type": "about:blank",
                    "title": NOT_USER,
                    "status": 0,
                    "detail": f"The users with uuid {uuid} was not found",
                    "instance": f"/users/{uuid}",
                }
            ),
            "code_status": 404,
        }


    """
    Create a users.
    In Flask: uuid.UUID is serialized to a string.
    """
    def create_users(self, request):
        if request.is_json:
            user = request.get_json()
            self.user_service.create(user)
            return jsonify({"data": user}), 201

        return {
            "response": jsonify(
                {
                    "type": "about:blank",
                    "title": BAD_REQUEST,
                    "status": 0,
                    "detail": f"{BAD_REQUEST} with body: {request}",
                    "instance": f"/users",
                }
            ),
            "code_status": 400,
       } 

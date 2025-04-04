from flask import jsonify

from headers import BAD_REQUEST, DELETE, NOT_USER, WRONG_PASSWORD
from src.application.user_service import UserService
from src.infrastructure.persistence.users_repository import UsersRepository
from werkzeug.security import check_password_hash

""" 
The presentation layer contains all of the classes responsible for presenting the UI to the end-user 
or sending the response back to the client (in case we’re operating deep in the back-end).

- It has serialization and deserialization logic. Validations. Authentication.
"""
class UserController:
    def __init__(self, user_service: UserService, logger): 
        self.user_service = user_service
        self.log = logger
        return
    

    def _serialize_user(self, user):
        return user.__dict__
    

    """
    Get all users.
    """
    def get_users(self):
        users = self.user_service.get_users() # list of instance of Users() (domain)
        users = [self._serialize_user(user) for user in users]
        self.log.debug(f"DEBUG: in controller: users is {users}")
        
        return {
            "response": jsonify({"data": users}), 
            "code_status": 200
        }
    

    """
    Get specific user.
    """
    def get_specific_users(self, uuid):
        user = self.user_service.get_specific_users(uuid) # instance of Users() (domain)

        if user:
            user = self._serialize_user(user)
            self.log.debug(f"DEBUG: user is {user}")
            return {
                "response": jsonify({"data": user}),
                "code_status": 200
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
    Delete user.
    """
    def delete_specific_users(self, uuid):
        if self.get_specific_users(uuid):
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
        print(f"DEBUG: request in create_users -> {request}", flush=True)

        if request.is_json:
            user = request.get_json()
            self.user_service.create(user)
            return {
                "response": jsonify({"data": user}),
                "code_status": 201
            }

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
    
    """
    Login users.
    """
    def login_users(self, request):
        if request.is_json:
            data = request.get_json()
            email = data["email"]
            password = data["password"]
            
            mail_exists = self.user_service.mail_exists(email)  
            
            if mail_exists is None:
                return {
                    "response": jsonify(
                        {
                            "type": "about:blank",
                            "title": NOT_USER,
                            "status": 0,
                            "detail": f"The email {email} was not found",
                            "instance": f"/users/login",
                        }
                    ),
                    "code_status": 404,
                }
            
            user_password = mail_exists[3] # this access the password
            if check_password_hash(user_password, password):
                # Do we need to return the user? . to ask
                return {
                    # Mail exists contain the user data.
                    "response": jsonify({"data": mail_exists}),
                    "code_status": 200
                }
            else:
                return {
                    "response": jsonify(
                        {
                            "type": "about:blank",
                            "title": WRONG_PASSWORD,
                            "status": 0,
                            "detail": f"The password is not correct",
                            "instance": f"/users/login",
                        }
                    ),
                    "code_status": 403,
                }
                         
        return {
            "response": jsonify(
                {
                    "type": "about:blank",
                    "title": BAD_REQUEST,
                    "status": 0,
                    "detail": f"{BAD_REQUEST} with body: {request}",
                    "instance": f"/users/login",
                }
            ),
            "code_status": 400,
       }

from flask import jsonify

from headers import BAD_REQUEST, DELETE, NOT_USER, PUT_LOCATION
from src.application.user_service import UserService
from src.infrastructure.persistence.users_repository import UsersRepository

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
        return {
            "uuid": user.uuid,
            "name": user.name,
            "surname": user.surname,
            "password": user.password,
            "email": user.email,
            "status": user.status,
            "role": user.role,
            "location": None if user.location is None else {  
                "latitude": user.location.latitude,
                "longitude": user.location.longitude
            } if user.location.latitude is not None and user.location.longitude is not None else None
        }

    
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
        self.log.debug(f"DEBUG: self.get_specific_users(uuid) delete -> {self.get_specific_users(uuid)}")

        if self.get_specific_users(uuid)["code_status"] == 204:
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
        self.log.debug(f"DEBUG: request in create_users -> {request}")

        if request.is_json:
            user = request.get_json()
            self.log.debug(f"DEBUG: json in create_users -> {user}")

            result, msg = self._check_create_user_params(user)
            if result == False:
                return {
                    "response": jsonify(
                        {
                            "type": "about:blank",
                            "title": BAD_REQUEST,
                            "status": 0,
                            "detail": f"{BAD_REQUEST}: {msg}",
                            "instance": f"/users",
                        }
                    ),
                    "code_status": 400,
                } 
            
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


    """Add location."""
    def set_user_location(self, user_id, request):
        data = request.get_json()
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        result, msg = self._check_location(latitude, longitude)
        if result == False:
            return {
                "response": jsonify(
                    {
                        "type": "about:blank",
                        "title": BAD_REQUEST,
                        "status": 0,
                        "detail": f"{BAD_REQUEST}: {msg}",
                        "instance": f"/users/<uuid:user_id>/location",
                    }
                ),
                "code_status": 400,
            } 

        if self.get_specific_users(user_id)["code_status"] == 204:
            self.log.debug("User exists")
            self.user_service.set_location(user_id, latitude, longitude)
            return {
                "response": jsonify({"result": PUT_LOCATION}),
                "code_status": 200
            }
        
        self.log.debug("User not exists")
        return {
            "response": jsonify(
                {
                    "type": "about:blank",
                    "title": NOT_USER,
                    "status": 0,
                    "detail": f"The users with uuid {user_id} was not found",
                    "instance": f"/users/{user_id}/location",
                }
            ),
            "code_status": 404,
        }

    def _check_location(self, latitude, longitude):

        if latitude is None or longitude is None:
            return False, "Location is required"
    
        try:
            lat = float(latitude)
            lon = float(longitude)

            if not (-90 <= lat <= 90):
                raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
            
            if not (-180 <= lon <= 180):
                raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")
            
            return True, "Ok."

        except (TypeError, ValueError) as e:
            msg = f"Invalid location data: {e}"
            self.log.error(msg)
            return False, msg


    def _check_create_user_params(self, user_params):
        missing_params = []

        for param in ["name", "surname", "password", "email", "status", "role"]: 
            if (not param in user_params) or (user_params[param] is None):
                missing_params.append(param)
                
        if len(missing_params) > 0:
            msg = f"Missing params: {", ".join(missing_params)}"
            self.log.error(msg)
            return False, msg
    
        return True, "Ok."

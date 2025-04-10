import os
from flask import jsonify, session

from src.headers import BAD_REQUEST, DELETE, NOT_USER, PUT_LOCATION, USER_ALREADY_EXISTS, WRONG_PASSWORD, ADMIN_AUTH_FAILED, ADMIN_CREATED, ADMIN_LOGIN_SUCCESS, ADMIN_LOGIN_FAILED
from src.application.user_service import UserService
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
        
        is_session_expired = self.is_session_valid()
        
        if is_session_expired:
            return is_session_expired
        
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
        
        is_session_expired = self.is_session_valid()
        
        if is_session_expired:
            return is_session_expired
        
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

        if self.get_specific_users(uuid)["code_status"] == 200:
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

            # Bloquea asignación manual de rol 'admin'
            if user.get("role") == "admin":
                return {
                    "response": jsonify({
                        "error": "Forbidden",
                        "detail": "Use /users/admin endpoint to create admins"
                    }),
                    "code_status": 403
                }

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
            
            # HOTFIX we cannot create a user with the same email
            mail_exists = self.user_service.mail_exists(user["email"])
            
            if mail_exists is not None:
                return {
                    "response": jsonify(
                        {
                            "type": "about:blank",
                            "title": USER_ALREADY_EXISTS,
                            "status": 0,
                            "detail": f"The email {user['email']} already exists",
                            "instance": f"/users",
                        }
                    ),
                    "code_status": 409,
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

        self.log.debug(f"DEBUG: self.get_specific_users(user_id) is {self.get_specific_users(user_id)}")

        if self.get_specific_users(user_id)["code_status"] == 200:
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
            msg = f"Missing params: {', '.join(missing_params)}"
            self.log.error(msg)
            return False, msg
    
        return True, "Ok."
    

    """
    Login users.
    """
    def login_users(self, request):
        if request.is_json:
            data = request.get_json()
             
            email = data['email'] # This contains mail 
            password = data['password'] # This contains password
            
            self.log.debug(f"DEBUG: email is {email}")
            self.log.debug(f"DEBUG: password is {password}")
                        
            # Check if the email and password are in the request
            # If this exists, this bring us the id of the user
            user_exists = self.user_service.mail_exists(email)

            if user_exists is None:
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
                            
            user_serialized_from_db = self.user_service.get_specific_users(user_exists) # we get the instance
            user_serialized_from_db = self._serialize_user(user_serialized_from_db) # Serialize the instance
            
            self.log.debug(f"DEBUG: user_serialized_from_db is {user_serialized_from_db}")
            
            if check_password_hash(user_serialized_from_db['password'], password):
                # Do we need to return the user? . to ask
                # We save the session for this email
                session["user"] = email 
                #session.permanent = True # This sets the session for 5 minutes (app.py - line 14)
                
                self.log.debug(f"DEBUG: User {email} logged in")
                self.log.debug(f"DEBUG: session is {session}")
                return {
                    # Mail exists contain the user data.
                    "response": jsonify({"data": user_serialized_from_db}),
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

    """
    Create an admin user.
    Authenticates the requester as an admin via email/password.
    """
    def create_admin_user(self, request):
        if not request.is_json:
            return {
                "response": jsonify({"error": BAD_REQUEST}),
                "code_status": 400
            }

        data = request.get_json()
        
        required_fields = [
            "admin_email", "admin_password",
            "name", "surname", "email", "password"
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {
                "response": jsonify({
                    "error": f"Missing fields: {', '.join(missing_fields)}"
                }),
                "code_status": 400
            }

        # Autentica al admin existente
        admin = self.user_service.mail_exists(data["admin_email"])
        if not admin or not check_password_hash(admin[3], data["admin_password"]):
            return {
                "response": jsonify({"error": ADMIN_AUTH_FAILED}),
                "code_status": 403
            }

        # Verifica que el autenticador sea admin
        if admin[6] != "admin":
            return {
                "response": jsonify({"error": ADMIN_AUTH_FAILED}),
                "code_status": 403
            }

        # Crea el nuevo admin
        new_user_data = {
            "name": data["name"],
            "surname": data["surname"],
            "email": data["email"],
            "password": data["password"],
            "status": "active",
            "role": "admin"
        }

        valid, msg = self._check_create_user_params(new_user_data)
        if not valid:
            return {
                "response": jsonify({"error": msg}),
                "code_status": 400
            }

        try:
            self.user_service.create(new_user_data)
            return {
                "response": jsonify({"message": ADMIN_CREATED}),
                "code_status": 201
            }
        except Exception as e:
            return {
                "response": jsonify({"error": str(e)}),
                "code_status": 500
            }


    """
    Login específico para administradores.
    """
    def login_admin(self, request):
        login_result = self.login_users(request)

        if login_result["code_status"] != 200:
            return login_result

        user_data = login_result["response"].get_json().get("data")
        session.permanent = False # This avoids the session to be saved for 5 minutes and keep it permanent

        # Verifica si es admin
        if user_data[6] == "admin":
            return {
                "response": jsonify({
                    "message": ADMIN_LOGIN_SUCCESS,
                    "data": user_data
                }),
                "code_status": 200
            }
        else:
            return {
                "response": jsonify({
                    "error": ADMIN_LOGIN_FAILED,
                    "detail": "User is not an admin"
                }),
                "code_status": 403
            }

    """
    Private function: This function checks if the session is still valid
    In case it isnt valid, it will return a 401 error
    else we return None
    """
    def is_session_valid(self):
        env = os.getenv("FLASK_ENV")
        if env == "testing":
            self.log.info("In TEST, without session expiration.")
            return None
        else:
            self.log.info("Check if the session has expired.")

        if "user" not in session:
            return {
                "response": jsonify({
                    "error": "Unauthorized",
                    "detail": "Session expired"
                }),
                "code_status": 401
            }
        return None

    """
    Login a user with google
    """
    def login_user_with_google(self):
        return self.user_service.login_user_with_google()


    def authorize(self):
        user_info = self.user_service.authorize()
        if user_info:
            user = self.user_service.create_users_if_not_exist(user_info)
            
            user_email = user['email']
            session['user'] = user_email
            return jsonify(user)
        
        return {
            "response": jsonify(
                {
                    "type": "about:blank",
                    "title": NOT_USER,
                    "status": 0,
                    "detail": f"User not authorized by Google",
                    "instance": f"/users/authorize",
                }
            ),
            "code_status": 404,
        }

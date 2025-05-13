import os
from flask import jsonify, session, current_app
from werkzeug.security import check_password_hash

from headers import (
    BAD_REQUEST,
    DELETE,
    NOT_USER,
    PUT_LOCATION,
    USER_ALREADY_EXISTS,
    WRONG_PASSWORD,
    ADMIN_AUTH_FAILED,
    ADMIN_CREATED,
    ADMIN_LOGIN_SUCCESS,
    ADMIN_LOGIN_FAILED,
)
from application.user_service import UserService
from presentation.error_generator import get_error_json


class UserController:
    """
    The presentation layer contains all of the classes responsible for presenting the UI to the end-user
    or sending the response back to the client (in case we’re operating deep in the back-end).

    - It has serialization and deserialization logic. Validations. Authentication.
    """

    def __init__(self, user_service: UserService):
        self.user_service = user_service
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
            "location": (
                None
                if user.location is None
                else (
                    {
                        "latitude": user.location.latitude,
                        "longitude": user.location.longitude,
                    }
                    if user.location.latitude is not None
                    and user.location.longitude is not None
                    else None
                )
            ),
        }

    def get_users(self):
        """
        Get all users.
        """

        is_session_expired = self.is_session_valid()

        if is_session_expired:
            return is_session_expired

        users = self.user_service.get_users()  # list of instance of Users() (domain)
        users = [self._serialize_user(user) for user in users]
        current_app.logger.debug(f"DEBUG: in controller: users is {users}")

        return {"response": jsonify({"data": users}), "code_status": 200}

    def get_specific_users(self, uuid):
        """
        Get specific user.
        """

        is_session_expired = self.is_session_valid()

        if is_session_expired:
            return is_session_expired

        user = self.user_service.get_specific_users(
            uuid
        )  # instance of Users() (domain)

        if user:
            user = self._serialize_user(user)
            current_app.logger.debug(f"DEBUG: user is {user}")
            return {"response": jsonify({"data": user}), "code_status": 200}

        return {
            "response": get_error_json(
                NOT_USER,
                f"The users with uuid {uuid} was not found",
                f"/users/<uuid:uuid>",
            ),
            "code_status": 404,
        }

    def delete_specific_users(self, uuid):
        """
        Delete user.
        """

        if self.get_specific_users(uuid)["code_status"] == 200:
            self.user_service.delete(uuid)
            return {"response": jsonify({"result": DELETE}), "code_status": 204}

        return {
            "response": get_error_json(
                NOT_USER,
                f"The users with uuid {uuid} was not found",
                f"/users/<uuid:uuid>",
                "DELETE",
            ),
            "code_status": 404,
        }

    def create_users(self, request):
        """
        Create a users.
        In Flask: uuid.UUID is serialized to a string.
        """
        current_app.logger.debug(f"DEBUG: request in create_users -> {request}")
        url = "/users"

        if request.is_json:
            user = request.get_json()
            current_app.logger.debug(f"DEBUG: json in create_users -> {user}")

            # Block manual assignment of the 'admin' role
            if user.get("role") == "admin":
                return {
                    "response": get_error_json(
                        "Forbidden",
                        "Use /users/admin endpoint to create admins",
                        url,
                        "POST",
                    ),
                    "code_status": 403,
                }

            result, msg = self._check_create_user_params(user)
            if result == False:
                return {
                    "response": get_error_json(BAD_REQUEST, msg, url, "POST"),
                    "code_status": 400,
                }

            # HOTFIX we cannot create a user with the same email
            mail_exists = self.user_service.mail_exists(user["email"])

            if mail_exists is not None:
                return {
                    "response": get_error_json(
                        USER_ALREADY_EXISTS,
                        f"The email {user['email']} already exists",
                        url,
                        "POST",
                    ),
                    "code_status": 409,
                }

            user = self.user_service.create(user)
            user = self._serialize_user(user)
            return {"response": jsonify({"data": user}), "code_status": 201}

        return {
            "response": get_error_json(
                BAD_REQUEST, f"with body: {request}", url, "POST"
            ),
            "code_status": 400,
        }

    def set_user_location(self, user_id, request):
        """Add location."""
        data = request.get_json()
        latitude = data.get("latitude")
        longitude = data.get("longitude")

        result, msg = self._check_location(latitude, longitude)
        if result == False:
            return {
                "response": get_error_json(
                    BAD_REQUEST, msg, f"/users/<uuid:user_id>/location", "POST"
                ),
                "code_status": 400,
            }

        if self.get_specific_users(user_id)["code_status"] == 200:
            current_app.logger.debug("User exists")
            self.user_service.set_location(user_id, latitude, longitude)
            return {"response": jsonify({"result": PUT_LOCATION}), "code_status": 200}

        current_app.logger.debug("User not exists")
        return {
            "response": get_error_json(
                NOT_USER,
                f"uuid {user_id} was not found",
                f"/users/<uuid:user_id>/location",
                "POST",
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
                raise ValueError(
                    f"Invalid latitude: {lat}. Must be between -90 and 90."
                )

            if not (-180 <= lon <= 180):
                raise ValueError(
                    f"Invalid longitude: {lon}. Must be between -180 and 180."
                )

            return True, "Ok."

        except (TypeError, ValueError) as e:
            msg = f"Invalid location data: {e}"
            return False, msg

    def _check_create_user_params(self, user_params):
        missing_params = []

        for param in ["name", "surname", "password", "email", "status", "role"]:
            if (not param in user_params) or (user_params[param] is None):
                missing_params.append(param)

        if len(missing_params) > 0:
            msg = f"Missing params: {', '.join(missing_params)}"
            return False, msg

        return True, "Ok."

    def login_users(self, request):
        """
        Login users.
        """
        url = "/users/login"
        if request.is_json:
            data = request.get_json()

            email = data["email"]  # This contains mail
            password = data["password"]  # This contains password

            current_app.logger.debug(f"DEBUG: email is {email}")
            current_app.logger.debug(f"DEBUG: password is {password}")

            # Check if the email and password are in the request
            # If this exists, this bring us the id of the user
            user_exists = self.user_service.mail_exists(email)

            if user_exists is None:
                return {
                    "response": get_error_json(
                        NOT_USER, f"The email {email} was not found", url, "POST"
                    ),
                    "code_status": 404,
                }

            user_serialized_from_db = self.user_service.get_specific_users(
                user_exists.uuid
            )  # we get the instance

            user_serialized_from_db = self._serialize_user(
                user_serialized_from_db
            )  # Serialize the instance

            current_app.logger.debug(
                f"DEBUG: user_serialized_from_db is {user_serialized_from_db}"
            )

            # First admin:
            if (
                user_serialized_from_db["role"] == "admin"
                and user_serialized_from_db["password"] == password
            ):
                session["user"] = email

                return {
                    "response": jsonify({"data": user_serialized_from_db}),
                    "code_status": 200,
                }

            if check_password_hash(user_serialized_from_db["password"], password):
                # Do we need to return the user? . to ask
                # We save the session for this email
                session["user"] = email
                # session.permanent = True # This sets the session for 5 minutes (app.py - line 14)

                current_app.logger.debug(f"DEBUG: User {email} logged in")
                current_app.logger.debug(f"DEBUG: session is {session}")
                return {
                    # Mail exists contain the user data.
                    "response": jsonify({"data": user_serialized_from_db}),
                    "code_status": 200,
                }
            else:
                return {
                    "response": get_error_json(
                        WRONG_PASSWORD, "The password is not correct", url, "POST"
                    ),
                    "code_status": 403,
                }

        return {
            "response": get_error_json(
                BAD_REQUEST, f"with body: {request}", url, "POST"
            ),
            "code_status": 400,
        }

    def create_admin_user(self, request):
        """
        Create an admin user.
        Authenticates the requester as an admin via email/password.
        """
        url = "/users/admin"
        if not request.is_json:
            return {
                "response": get_error_json(
                    BAD_REQUEST, f"{request} is not json", url, "POST"
                ),
                "code_status": 400,
            }

        data = request.get_json()

        required_fields = [
            "admin_email",
            "admin_password",
            "name",
            "surname",
            "email",
            "password",
        ]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return {
                "response": get_error_json(
                    BAD_REQUEST,
                    f"Missing fields: {', '.join(missing_fields)}",
                    url,
                    "POST",
                ),
                "code_status": 400,
            }

        # Autentica al admin existente
        admin = self.user_service.mail_exists(data["admin_email"])
        if not admin or not check_password_hash(admin.email, data["admin_password"]):
            return {
                "response": get_error_json(
                    ADMIN_AUTH_FAILED,
                    "not admin or not check password hash",
                    url,
                    "POST",
                ),
                "code_status": 403,
            }

        # Verifica que el autenticador sea admin
        if admin.role != "admin":
            return {
                "response": get_error_json(
                    ADMIN_AUTH_FAILED, f"role {admin.role} is not admin", url, "POST"
                ),
                "code_status": 403,
            }

        # Crea el nuevo admin
        new_user_data = {
            "name": data["name"],
            "surname": data["surname"],
            "email": data["email"],
            "password": data["password"],
            "status": "active",
            "role": "admin",
        }

        valid, msg = self._check_create_user_params(new_user_data)
        if not valid:
            return {
                "response": get_error_json("Error in params", msg, url, "POST"),
                "code_status": 400,
            }

        try:
            self.user_service.create(new_user_data)
            return {"response": jsonify({"message": ADMIN_CREATED}), "code_status": 201}
        except Exception as e:
            return {
                "response": get_error_json(
                    "Error in: user service - create", str(e), url, "POST"
                ),
                "code_status": 500,
            }

    def login_admin(self, request):
        """
        Login específico para administradores.
        """
        login_result = self.login_users(request)

        if login_result["code_status"] != 200:
            return login_result

        user_data = login_result["response"].get_json().get("data")

        # Verifica si es admin
        if user_data["role"] == "admin":
            # Session created, we assign whatever for this session, we dont care
            session["user"] = user_data
            session.permanent = True  # this sets the session permanent
            current_app.logger.debug(f"DEBUG: session is {session}")
            return {
                "response": jsonify(
                    {"message": ADMIN_LOGIN_SUCCESS, "data": user_data}
                ),
                "code_status": 200,
            }
        else:
            return {
                "response": get_error_json(
                    ADMIN_LOGIN_FAILED,
                    f"role {user_data[6]} is not 'admin'",
                    "/users/admin/login",
                    "POST",
                ),
                "code_status": 403,
            }

    def is_session_valid(self):
        """
        Private function: This function checks if the session is still valid
        In case it isnt valid, it will return a 401 error
        else we return None
        """
        env = os.getenv("FLASK_ENV")
        if env == "testing":
            current_app.logger.info("In TEST, without session expiration.")
            return None
        else:
            current_app.logger.info("Check if the session has expired.")

        if "user" not in session or not session.permanent:
            current_app.logger.info(f"Session: {session}")
            current_app.logger.info("Session not valid.")
            return {
                "response": get_error_json("Unauthorized", "Session expired", "/users"),
                "code_status": 401,
            }
        return None

    def login_user_with_google(self, request):
        """
        Login a user with google
        """
        current_app.logger.info(f"In controller with request: {request}")
        role = request.args.get("role", "student")
        current_app.logger.info(f"In controller - role: {role}")
        return self.user_service.login_user_with_google(role)

    def authorize(self, request):
        user_info = self.user_service.authorize()
        current_app.logger.info(f"In controller - user_info: {user_info}")

        if user_info:
            user_info["role"] = request.args.get("state", "student")
            user_info["status"] = "enabled"
            user = self.user_service.create_users_if_not_exist(user_info)
            user = self._serialize_user(user)
            current_app.logger.debug(f"In controller - user: {user}")

            user_email = user["email"]
            session["user"] = user_email
            return {"response": jsonify({"data": user}), "code_status": 200}

        return {
            "response": get_error_json(
                NOT_USER, "User not authorized by Google", "/users/authorize"
            ),
            "code_status": 404,
        }

    def authorize_with_token(self, request):
        data = request.get_json()
        current_app.logger.debug(f"Data: {data}")
        token = data.get("token")

        user_info = self.user_service.verify_google_token(token)
        if not user_info:
            return {
                "response": get_error_json(
                    NOT_USER, "Token inválido", "/users/authorize"
                ),
                "code_status": 401,
            }

        data["role"] = data.get("role", "student")
        data["status"] = data.get("status", "enabled")
        user = self.user_service.create_users_if_not_exist(data)
        user = self._serialize_user(user)

        return {"response": jsonify({"data": user}), "code_status": 200}

    def authorize_signup_token(self, request):
        """
        request should have: token, role, email_verified, email, given_name, family_name, photo
        """
        params = [
            "token",
            "email_verified",
            "email",
            "given_name",
            "family_name",
            "photo",
            "role",
        ]
        data = request.get_json()
        current_app.logger.debug(f"Data: {data}")
        if self._validate_request(data, params) == False:
            return {
                "response": get_error_json(
                    BAD_REQUEST, "Request should have {params}", "/users/signup/google"
                ),
                "code_status": 401,
            }

        token = data.get("token")
        user_info = self.user_service.verify_google_token(token)
        if not user_info:
            return {
                "response": get_error_json(
                    NOT_USER, "Token inválido", "/users/signup/google"
                ),
                "code_status": 401,
            }

        data["role"] = data.get("role", "student")
        data["status"] = data.get("status", "enabled")
        user = self.user_service.create_users(data)
        user = self._serialize_user(user)

        return {"response": jsonify({"data": user}), "code_status": 200}

    def authorize_login_token(self, request):
        """
        request should have: token, email_verified, email, given_name, family_name, photo.
        If the status is "disabled" in db, user is not returned. User locked error is returned.
        """
        params = [
            "token",
            "email_verified",
            "email",
            "given_name",
            "family_name",
            "photo",
        ]
        data = request.get_json()
        current_app.logger.debug(f"Data: {data}")

        if self._validate_request(data, params) == False:
            return {
                "response": get_error_json(
                    BAD_REQUEST, "Request should have {params}", "/users/login/google"
                ),
                "code_status": 401,
            }

        token = data.get("token")
        user_info = self.user_service.verify_google_token(token)
        if user_info:
            user = self.user_service.verify_user_existence(data)
            if user != None:
                if user.status == "enabled":
                    user = self._serialize_user(user)

                    return {"response": jsonify({"data": user}), "code_status": 200}
                else:
                    detail = "User desabled"
            else:
                detail = "User not exist"
        else:
            detail = "Token invalid"

        return {
            "response": get_error_json(NOT_USER, detail, "/users/login/google"),
            "code_status": 401,
        }

    def _validate_request(self, request, params):
        for param in params:
            if param not in request:
                return False
        True

    def initiate_password_recovery(self, email):
        """Controlador para el inicio de recuperación de contraseña"""
        try:
            result = self.user_service.initiate_password_recovery(email)
            if "pin" in result:  # Si hay PIN en la respuesta
                return {
                    "response": jsonify(
                        {
                            "message": result["message"],
                            "pin": result["pin"],  # ← Asegurar que el PIN se incluye
                        }
                    ),
                    "code_status": result["code"],
                }
            return {
                "response": jsonify({"message": result["error"]}),
                "code_status": result["code"],
            }
        except Exception as e:
            current_app.logger.error(f"Error en recuperación de contraseña: {str(e)}")
            return {
                "response": jsonify(
                    {"error": "Ocurrió un error al procesar la solicitud"}
                ),
                "code_status": 500,
            }

    def validate_recovery_pin(self, email: str, pin_code: str) -> dict:
        """Controlador para validación de PIN"""
        try:
            result = self.user_service.validate_recovery_pin(email, pin_code)
            return {
                "response": jsonify(
                    {"message": result["message"]}
                    if "message" in result
                    else {"error": result["error"]}
                ),
                "code_status": result["code"],
            }
        except Exception as e:
            current_app.logger.error(f"Error validando PIN: {str(e)}")
            return {
                "response": jsonify({"error": "Error validando PIN"}),
                "code_status": 500,
            }

    def update_password(self, email, new_password):
        """Controlador para actualización de contraseña"""
        try:
            result = self.user_service.update_password(email, new_password)
            return {
                "response": jsonify(
                    {"message": result["message"]}
                    if "message" in result
                    else {"error": result["error"]}
                ),
                "code_status": result["code"],
            }
        except Exception as e:
            current_app.logger.error(f"Error actualizando contraseña: {str(e)}")
            return {
                "response": jsonify({"error": "Error actualizando contraseña"}),
                "code_status": 500,
            }

    def initiate_registration_confirmation(self, email: str) -> dict:
        """Controlador para inicio de confirmación de registro"""
        try:
            result = self.user_service.initiate_registration_confirmation(email)
            if "pin" in result:
                return {
                    "response": jsonify(
                        {"message": result["message"], "pin": result["pin"]}
                    ),
                    "code_status": result["code"],
                }
            return {
                "response": jsonify({"error": result["error"]}),
                "code_status": result["code"],
            }
        except Exception as e:
            current_app.logger.error(f"Error en confirmación de registro: {str(e)}")
            return {
                "response": jsonify(
                    {"error": "Ocurrió un error al procesar la solicitud"}
                ),
                "code_status": 500,
            }

    def validate_registration_pin(self, email, pin_code):
        """Controlador para validación de PIN de registro"""
        try:
            result = self.user_service.validate_registration_pin(email, pin_code)
            return {
                "response": jsonify(
                    {"message": result["message"]}
                    if "message" in result
                    else {"error": result["error"]}
                ),
                "code_status": result["code"],
            }
        except Exception as e:
            current_app.logger.error(f"Error validando PIN de registro: {str(e)}")
            return {
                "response": jsonify({"error": "Error validando PIN de registro"}),
                "code_status": 500,
            }

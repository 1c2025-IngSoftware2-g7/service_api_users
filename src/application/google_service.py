import os
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import current_app

USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleService:
    def __init__(self, oauth):
        self.client_id = os.getenv("GOOGLE_CLIENT_ID")
        self.google = oauth.register(
            name="google",
            client_id=self.client_id,
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_kwargs={"scope": "openid email profile"},
        )

    def authorize_redirect(self, role):
        current_app.logger.info(f"In google service - role: {role}")
        redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
        current_app.logger.info(f"In google service - redirect_uri: {redirect_uri}")
        return self.google.authorize_redirect(redirect_uri, state=role)

    def authorize_access_token(self):
        return self.google.authorize_access_token()

    def get_user_info(self):
        response = self.google.get(USERINFO_URL)
        current_app.logger.info(f"In google service - get_user_info - response: {response}")
        return response.json()

    def verify_google_token(self, id_token_str):
        """
        This method validates the token, decodes it and returns the user info
        """
        try:
            id_info = id_token.verify_oauth2_token(
                id_token_str, requests.Request(), audience=self.client_id
            )

            if id_info["email_verified"]:
                email = id_info["email"]
                name = id_info.get("name")
                picture = id_info.get("picture")
                sub = id_info.get("sub")  # Unique user ID on Google

                return {
                    "email": email,
                    "name": name,
                    "picture": picture,
                    "google_id": sub,
                }

            else:
                raise ValueError("Unverified email")

        except ValueError as e:
            current_app.logger.error(f"Invalid token: {e}")
            return None

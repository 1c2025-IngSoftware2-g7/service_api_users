import os

USERINFO_URL = "https://openidconnect.googleapis.com/v1/userinfo"


class GoogleService:
    def __init__(self, oauth, logger):
        self.log = logger
        self.google = oauth.register(
            name='google',
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
            client_kwargs={'scope': 'openid email profile'},
        )
    
    def authorize_redirect(self, role):
        self.log.info(f"In google service - role: {role}")
        redirect_uri = os.getenv("OAUTH_REDIRECT_URI")
        self.log.info(f"In google service - redirect_uri: {redirect_uri}")
        return self.google.authorize_redirect(redirect_uri, state=role)


    def authorize_access_token(self):
        return self.google.authorize_access_token()
    
    def get_user_info(self):
        response = self.google.get(USERINFO_URL)
        self.log.info(f"In google service - get_user_info - response: {response}")
        return response.json()

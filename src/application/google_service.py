import os
from flask import Flask, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth


class GoogleService:
    def __init__(self, oauth):
        self.google = oauth.register(
            name='google',
            client_id=os.getenv("GOOGLE_CLIENT_ID"),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
            access_token_url='https://accounts.google.com/o/oauth2/token',
            access_token_params=None,
            authorize_url='https://accounts.google.com/o/oauth2/auth',
            authorize_params=None,
            api_base_url='https://www.googleapis.com/oauth2/v1/',
            userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
            client_kwargs={'scope': 'openid email profile'},
            redirect_uri=os.getenv("OAUTH_REDIRECT_URI"),
        )
    
    def authorize_redirect(self):
        return self.google.authorize_redirect()

    def authorize_access_token(self):
        return self.google.authorize_access_token()
    
    def get_user_info(self):
        response = self.google.get('userinfo')
        return response.json()


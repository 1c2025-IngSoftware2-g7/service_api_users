from flask import current_app

from infrastructure.persistence.users_repository import UsersRepository


""" 
The application layer contains all the logic that is required by the application to meet its functional requirements and, 
at the same time, is not a part of the domain rules. In most systems that I've worked with, the application layer consisted 
of services orchestrating the domain objects to fulfill a use case scenario.

This layer can include:
- Service Application
- Use Case
- Interacting between domains
- Functions for each feature of our API using domain entities
- Entry points to the domain
- Communicates with the repository layer, which can return a User domain
"""


class UserService:
    def __init__(self, user_repository: UsersRepository, google):
        self.google = google
        self.user_repository = user_repository

    def get_users(self):
        """Get all users."""
        users = self.user_repository.get_all_users()
        return users

    def get_specific_users(self, uuid):
        """Get specific user."""
        user = self.user_repository.get_user(uuid)
        return user

    def delete(self, uuid):
        """Delete user."""
        self.user_repository.delete_users(uuid)
        return

    def create(self, request):
        """Create a users."""
        self.user_repository.insert_user(request)
        return self.user_repository.get_user_with_email(request["email"])

    def set_location(self, uuid, latitude, longitude):
        """Add location."""
        self.user_repository.set_location(
            {"uuid": uuid, "latitude": latitude, "longitude": longitude}
        )
        return

    def mail_exists(self, email):
        """  Function that check if a mail is valid on the database. If it is, we return the the user."""
        return self.user_repository.get_user_with_email(email)

    def login_user_with_google(self, role):
        """Login a user with google."""
        current_app.logger.info(f"In service - login_user_with_google - role: {role}")
        return self.google.authorize_redirect(role)

    def authorize(self):
        token = self.google.authorize_access_token()
        current_app.logger.info(f"In service - authorize - token: {token}")
        return self.google.get_user_info()

    def create_users_if_not_exist(self, user_info):
        user = self.user_repository.get_user_with_email(user_info["email"])
        current_app.logger.info(f"In service - create_users_if_not_exist - user: {user}")
        if user != None:
            return user

        current_app.logger.info(
            f"User does not exist. Create user with the following parameters: {user_info}"
        )

        self.user_repository.insert_user(user_info)
        user = self.user_repository.get_user_with_email(user_info["email"])
        return user

    def verify_user_existence(self, user_info):
        user = self.user_repository.get_user_with_email(user_info["email"])
        current_app.logger.info(f"In service - create_users_if_not_exist - user: {user}")
        return user

    def create_users(self, user_info):
        user = self.user_repository.get_user_with_email(user_info["email"])
        current_app.logger.info(f"In service - create_users - user: {user}")
        if user != None:
            return user

        current_app.logger.info(
            f"User does not exist. Create user with the following parameters: {user_info}"
        )

        self.user_repository.insert_user(user_info)
        user = self.user_repository.get_user_with_email(user_info["email"])
        return user

    def verify_google_token(self, token):
        return self.google.verify_google_token(token)

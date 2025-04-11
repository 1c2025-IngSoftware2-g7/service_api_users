from src.application.google_service import GoogleService
from src.infrastructure.persistence.users_repository import UsersRepository

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
    def __init__(self, user_repository: UsersRepository, google, logger):
        self.google = google
        self.log = logger
        self.user_repository = user_repository


    """Get all users."""
    def get_users(self):
        users = self.user_repository.get_all_users()
        return users


    """
    Get specific user.
    """
    def get_specific_users(self, uuid):
        user = self.user_repository.get_user(uuid)
        return user


    """
    Delete user.
    """
    def delete(self, uuid):
        self.user_repository.delete_users(uuid)
        return


    """
    Create a users.
    """
    def create(self, request):
        self.user_repository.insert_user(request)
        return


    """
    Add location.
    """
    def set_location(self, uuid, latitude, longitude):
        self.user_repository.set_location(
            {"uuid": uuid, "latitude": latitude, "longitude": longitude}
        )
        return
    
    
    """ 
    Function that check if a mail is valid on the database
    If it is, we return the id from the user"""
    def mail_exists(self, email):
        return self.user_repository.check_email(email)

    """
    Login a user with google
    """
    def login_user_with_google(self, role):
        self.log.info(f"In service - login_user_with_google - role: {role}")
        return self.google.authorize_redirect(role)
    
    def authorize(self):
        token = self.google.authorize_access_token()
        self.log.info(f"In service - authorize - token: {token}")
        return self.google.get_user_info()
        
    
    def create_users_if_not_exist(self, user_info):
        user = self.user_repository.get_user_with_email(user_info['email'])
        self.log.info(f"In service - create_users_if_not_exist - user: {user}")
        if user:
            return user
    
        self.log.info(f"User does not exist. Create user with the following parameters: {user_info}")
        
        self.user_repository.insert_user(user_info)
        return user_info

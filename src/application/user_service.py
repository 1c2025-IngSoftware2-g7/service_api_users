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
    def __init__(self, user_repository: UsersRepository, logger):
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

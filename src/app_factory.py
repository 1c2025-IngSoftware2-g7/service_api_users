from application.google_service import GoogleService
from application.user_service import UserService
from infrastructure.persistence.users_repository import UsersRepository
from presentation.user_controller import UserController


class AppFactory:
    """Each class is instantiate: presentation, infrastructure, controller."""
    @staticmethod
    def create(oauth):
        user_repository = UsersRepository()
        google = GoogleService(oauth)
        user_service = UserService(user_repository, google)
        user_controller = UserController(user_service)
        return user_controller

from src.application.google_service import GoogleService
from src.application.user_service import UserService
from src.infrastructure.persistence.users_repository import UsersRepository
from src.presentation.user_controller import UserController

"""Each class is instantiate: presentation, infrastructure, controller."""


class AppFactory:
    @staticmethod
    def create(logger, oauth):
        user_repository = UsersRepository(logger)
        google = GoogleService(oauth, logger)
        user_service = UserService(user_repository, google, logger)
        user_controller = UserController(user_service, logger)
        return user_controller

from application.user_service import UserService
from infrastructure.persistence.users_repository import UsersRepository
from presentation.user_controller import UserController

"""Each class is instantiate: presentation, infrastructure, controller."""
class AppFactory:
    @staticmethod
    def create(logger):
        user_repository = UsersRepository(logger)
        user_service = UserService(user_repository, logger)
        user_controller = UserController(user_service, logger)
        return user_controller

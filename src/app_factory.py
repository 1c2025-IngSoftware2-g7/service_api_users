from application.user_service import UserService
from infrastructure.persistence.users_repository import UsersRepository
from presentation.user_controller import UserController

"""Each class is instantiate: presentation, infrastructure, controller."""
class AppFactory:
    @staticmethod
    def create():
        user_repository = UsersRepository()
        user_service = UserService(user_repository)
        user_controller = UserController(user_service)
        return user_controller

from infrastructure.config.db_config import DatabaseConfig
from infrastructure.persistence.base_entity import BaseEntity
from src.domain.user import User
from werkzeug.security import generate_password_hash

class UsersRepository(BaseEntity):
    def __init__(self, logger):
        self.log = logger
        super().__init__()


    def _parse_user(self, user_params):
        self.log.debug(f"DEBUG: user_params is {user_params}")
        return User(
            user_params["uuid"], 
            user_params["name"], 
            user_params["surname"], 
            user_params["password"], 
            user_params["email"], 
            user_params["status"], 
            user_params["role"]
        )


    def get_all_users(self):
        query = "SELECT ROW_TO_JSON(u) FROM users u"
        self.cursor.execute(query)
        users = self.cursor.fetchall()
        self.log.debug(f"DEBUG: users is {users}")

        # Returns an instance of the domain:
        result = []
        for user in users:
            result.append(self._parse_user(user[0]))
        return result
    
    def get_user(self, user_id):
        query = "SELECT ROW_TO_JSON(u) FROM users u WHERE uuid = %s"
        params = (str(user_id),)
        self.cursor.execute(query, params = params)
        user = self.cursor.fetchone()
        return self._parse_user(user[0])
    
    def insert_user(self, params_new_user):
        query = "INSERT INTO users (name, surname, password, email, status, role) VALUES (%s, %s, %s, %s, %s, %s)"
        
        password_hashed = generate_password_hash(params_new_user["password"])
        
        params = (
            params_new_user["name"], 
            params_new_user["surname"], 
            password_hashed, 
            params_new_user["email"], 
            params_new_user["status"], 
            params_new_user["role"]
        )
        self.cursor.execute(query, params = params)
        self.conn.commit()
        return

    def delete_users(self, user_id):
        query = "DELETE FROM users WHERE uuid = %s"
        params = (str(user_id),)
        self.cursor.execute(query, params = params)
        self.conn.commit()
        return
    
    """ 
    Function that check if a mail is valid on the database
    returns the user if it exists
    else returns None
    """
    def check_email(self, email):
        query = "SELECT * FROM users u WHERE email = %s"
        params = (email,)
        
        self.cursor.execute(query, params = params)
        
        user = self.cursor.fetchone()
        
        if user:
            return user
        
        return None
    
        

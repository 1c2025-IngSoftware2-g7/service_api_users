from infrastructure.persistence.base_entity import BaseEntity
from src.domain.user import User

class UsersRepository(BaseEntity):
    def _parse_user(self, user_params):
        return User(user_params["uuid"], user_params["name"], user_params["surname"], user_params["password"], user_params["email"], user_params["status"], user_params["role"])


    def get_all_users(self):
        query = "SELECT * FROM users ORDER BY publication_date DESC"
        self.cursor.execute(query)
        users = self.cursor.fetchall()

        # Returns an instance of the domain:
        result = []
        for user in users:
            result.append(self._parse_user(user))
        return result
    
    def get_user(self, user_id):
        query = "SELECT * FROM users WHERE uuid = %s"
        params = (str(user_id),)
        self.cursor.execute(query, params = params)
        user = self.cursor.fetchall()
        return self._parse_user(user)
    
    def insert_user(self, params_new_course):
        query = "INSERT INTO users (uuid, name, surname, password, email, status, role) VALUES (%s, %s, %s)"
        params = (str(params_new_course["uuid"]), params_new_course["title"], params_new_course["description"])
        self.cursor.execute(query, params = params)
        self.conn.commit()
        return

    def delete_users(self, user_id):
        query = "DELETE FROM users WHERE uuid = %s"
        params = (str(user_id),)
        self.cursor.execute(query, params = params)
        self.conn.commit()
        return

from domain.location import Location
from infrastructure.config.db_config import DatabaseConfig
from infrastructure.persistence.base_entity import BaseEntity
from src.domain.user import User

class UsersRepository(BaseEntity):
    def __init__(self, logger):
        self.log = logger
        super().__init__()


    def _parse_user(self, user_params):
        self.log.debug(f"DEBUG: user_params is {user_params}")

        location = None
        if "location" in user_params and user_params["location"] is not None:
            location = Location(
                user_params["location"].get("latitude"),
                user_params["location"].get("longitude"),
            )

        return User(
            user_params["uuid"], 
            user_params["name"], 
            user_params["surname"], 
            user_params["password"], 
            user_params["email"], 
            user_params["status"], 
            user_params["role"],
            location
        )


    def get_all_users(self):
        query = """
        SELECT ROW_TO_JSON(user_data) 
        FROM (
            SELECT 
                u.uuid,
                u.name,
                u.surname,
                u.password,
                u.email,
                u.status,
                u.role,
                JSON_BUILD_OBJECT(
                    'latitude', l.latitude,
                    'longitude', l.longitude
                ) AS location
            FROM users u
            LEFT JOIN user_locations l ON u.uuid = l.uuid
        ) AS user_data;
        """
        self.cursor.execute(query)
        users = self.cursor.fetchall()
        self.log.debug(f"DEBUG: users is {users}")

        # Returns an instance of the domain:
        result = []
        for user in users:
            result.append(self._parse_user(user[0]))
        return result
    
    def get_user(self, user_id):
        query = """
        SELECT ROW_TO_JSON(user_data) 
        FROM (
            SELECT 
                u.uuid,
                u.name,
                u.surname,
                u.password,
                u.email,
                u.status,
                u.role,
                JSON_BUILD_OBJECT(
                    'latitude', l.latitude,
                    'longitude', l.longitude
                ) AS location
            FROM users u
            LEFT JOIN user_locations l ON u.uuid = l.uuid
            WHERE u.uuid = %s
        ) AS user_data;
        """
        params = (str(user_id),)
        self.cursor.execute(query, params = params)
        user = self.cursor.fetchone()
        if not user:
            return user
        return self._parse_user(user[0])
    
    def insert_user(self, params_new_user):
        query = "INSERT INTO users (name, surname, password, email, status, role) VALUES (%s, %s, %s, %s, %s, %s)"
        params = (
            params_new_user["name"], 
            params_new_user["surname"], 
            params_new_user["password"], 
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
    Try inserting a new row into the user_locations table.
    If the UUID already exists (primary key conflict), then update the latitude and longitude.
    """
    def set_location(self, params_new_user):
        query = """
        INSERT INTO user_locations (uuid, latitude, longitude)
        VALUES (%s, %s, %s)
        ON CONFLICT (uuid)
        DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude;
        """
        params = (
            params_new_user["uuid"], 
            params_new_user["longitude"],
            params_new_user["latitude"], 
        )
        self.cursor.execute(query, params = params)
        self.conn.commit()
        return

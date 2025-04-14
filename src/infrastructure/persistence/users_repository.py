from domain.location import Location
from infrastructure.persistence.base_entity import BaseEntity
from domain.user import User
from werkzeug.security import generate_password_hash


class UsersRepository(BaseEntity):
    def __init__(self, logger):
        self.log = logger
        super().__init__()

    def _parse_user(self, user_params):
        self.log.debug(f"user_params is {user_params}")

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
            location,
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
        print(f"-----  ACAAAAA : {users}")

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
        self.cursor.execute(query, params=params)
        user = self.cursor.fetchone()
        if not user:
            return user
        return self._parse_user(user[0])

    def get_user_with_email(self, email):
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
            WHERE u.email = %s
        ) AS user_data;
        """
        params = (str(email),)
        self.cursor.execute(query, params=params)
        user = self.cursor.fetchone()
        if not user:
            return None
        return self._parse_user(user[0])

    def insert_user(self, params_new_user):
        query = "INSERT INTO users (name, surname, password, email, status, role) VALUES (%s, %s, %s, %s, %s, %s)"
        params = self._get_params_to_insert(params_new_user)

        self.cursor.execute(query, params=params)
        self.conn.commit()
        return

    def _get_params_to_insert(self, params_new_user):
        if "email_verified" in params_new_user:  # log in with google
            name = params_new_user["given_name"]
            surname = params_new_user["family_name"]
        else:
            name = params_new_user["name"]
            surname = params_new_user["surname"]

        if "password" in params_new_user:
            password = generate_password_hash(params_new_user["password"])
        else:
            password = generate_password_hash(params_new_user["token"])

        return (
            name,
            surname,
            password,
            params_new_user["email"],
            params_new_user["status"],
            params_new_user["role"],
        )

    def delete_users(self, user_id):
        query = "DELETE FROM users WHERE uuid = %s"
        params = (str(user_id),)
        self.cursor.execute(query, params=params)
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
            params_new_user["latitude"],
            params_new_user["longitude"],
        )
        self.cursor.execute(query, params=params)
        self.conn.commit()
        return

    """ 
    Function that check if a mail is valid on the database
    returns the id of the user if it exists
    else returns None
    """

    def check_email(self, email):
        query = "SELECT * FROM users u WHERE email = %s"
        params = (email,)

        self.cursor.execute(query, params=params)

        user = self.cursor.fetchone()

        if user:
            id = user[0]  # We get the ID and we return it as STR
            return id

        return None

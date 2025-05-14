import pytest
import uuid
from unittest.mock import MagicMock, patch
from domain.user import User
from infrastructure.persistence.users_repository import UsersRepository

@pytest.fixture
def password_hash():
    with patch("infrastructure.persistence.users_repository.generate_password_hash") as mock_hash:
        mock_hash.return_value = "hashed-password"
        yield


@pytest.fixture
def uuid_1():
    return uuid.uuid4()

@pytest.fixture
def uuid_2():
    return uuid.uuid4()

@pytest.fixture
def mock_cursor():
    cursor = MagicMock()
    cursor.execute = MagicMock()
    cursor.fetchall = MagicMock()
    cursor.fetchone = MagicMock()
    return cursor


@pytest.fixture
def mock_db_connection(mock_cursor):
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    return conn

""" Simulate the database connection in the constructor """
@pytest.fixture
def users_repository(mock_db_connection):
    repository = UsersRepository()
    repository.conn = mock_db_connection
    repository.cursor = mock_db_connection.cursor()
    return repository


def test_get_all_users(users_repository, mock_cursor, uuid_1, uuid_2, password_hash):
    mock_cursor.fetchall.return_value = [
        ({
            "uuid": str(uuid_1),
            "name": "Juan",
            "surname": "Perez",
            "password": "password",
            "email": "juan.perez@gmail.com",
            "status": "active",
            "role": "admin",
            "location": {"latitude": 45.04, "longitude": -75.00},
        },),
        ({
            "uuid": str(uuid_2),
            "name": "Juana",
            "surname": "Lopez",
            "password": "password",
            "email": "juana.lopez@gmail.com",
            "status": "active",
            "role": "user",
            "location": {"latitude": 34.0522, "longitude": -118.2437},
        },),
    ]

    
    users = users_repository.get_all_users()

    assert len(users) == 2
    assert isinstance(users[0], User)
    assert users[0].uuid == str(uuid_1)
    assert users[1].location.latitude == 34.0522


def test_get_user(users_repository, mock_cursor, uuid_1, password_hash):
    mock_cursor.fetchone.return_value = ({
        "uuid": str(uuid_1),
        "name": "Juan",
        "surname": "Perez",
        "password": "password",
        "email": "juan.perez@gmail.com",
        "status": "active",
        "role": "admin",
        "location": {"latitude": 45.04, "longitude": -75.00},
    },)
    
    user = users_repository.get_user(str(uuid_1))

    assert isinstance(user, User)
    assert user.uuid == str(uuid_1)
    assert user.name == 'Juan'


def test_get_user_with_email(users_repository, mock_cursor, uuid_1):
    mock_cursor.fetchone.return_value = ({
        "uuid": str(uuid_1),
        "name": "Juan",
        "surname": "Perez",
        "password": "password",
        "email": "juan.perez@gmail.com",
        "status": "active",
        "role": "admin",
        "location": {"latitude": 45.04, "longitude": -75.00},
    },)

    user = users_repository.get_user_with_email("juan.perez@gmail.com")

    assert isinstance(user, User)
    assert user.email == 'juan.perez@gmail.com'


def test_insert_user(users_repository, mock_cursor, password_hash):
    params_new_user = {
        'name': 'Juan',
        'surname': 'Perez',
        'password': "hashed-password",
        'email': 'juan.perez@gmail.com',
        'status': 'active',
        'role': 'admin'
    }

    users_repository.insert_user(params_new_user)

    mock_cursor.execute.assert_called_once_with(
        'INSERT INTO users (name, surname, password, email, status, role) VALUES (%s, %s, %s, %s, %s, %s)',
        params=('Juan', 'Perez', "hashed-password", 'juan.perez@gmail.com', 'active', 'admin')
    )


def test_set_location(users_repository, mock_cursor, uuid_1):
    params_new_user = {
        'uuid': uuid_1,
        'latitude': 45.04,
        'longitude': -75.00
    }

    users_repository.set_location(params_new_user)

    mock_cursor.execute.assert_called_once_with(
        """
        INSERT INTO user_locations (uuid, latitude, longitude)
        VALUES (%s, %s, %s)
        ON CONFLICT (uuid)
        DO UPDATE SET
            latitude = EXCLUDED.latitude,
            longitude = EXCLUDED.longitude;
        """,
        params=(uuid_1, 45.04, -75.00)
    )


def test_check_email(users_repository, mock_cursor, uuid_1):
    mock_cursor.fetchone.return_value = ({
        "uuid": str(uuid_1),
        "name": "Juan",
        "surname": "Perez",
        "password": "password",
        "email": "juan.perez@gmail.com",
        "status": "active",
        "role": "admin",
        "location": {"latitude": 45.04, "longitude": -75.00},
    },)

    user_id = users_repository.check_email('juan.perez@gmail.com')

    assert user_id["uuid"] == str(uuid_1)
    mock_cursor.execute.assert_called_once_with(
        "SELECT * FROM users u WHERE email = %s",
        params=('juan.perez@gmail.com',)
    )


def test_delete_user(users_repository, mock_cursor, uuid_1):
    user_id = uuid_1

    users_repository.delete_users(user_id)

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM users WHERE uuid = %s",
        params=(str(uuid_1),)
    )

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
def mock_db_connection_and_cursor():
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    with patch("infrastructure.persistence.base_entity.BaseEntity.connect_with_retries", return_value=mock_conn):
        yield mock_conn, mock_cursor

@pytest.fixture
def users_repository(mock_db_connection_and_cursor):
    repository = UsersRepository()
    # Ya la conexión y cursor están mockeados por patch
    return repository

def test_get_all_users(users_repository, mock_db_connection_and_cursor, uuid_1, uuid_2):
    _, mock_cursor = mock_db_connection_and_cursor
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


def test_get_user(users_repository, mock_db_connection_and_cursor, uuid_1, password_hash):
    _, mock_cursor = mock_db_connection_and_cursor
    mock_cursor.fetchone.return_value = ({
        "uuid": str(uuid_1),
        "name": "Juan",
        "surname": "Perez",
        "password": password_hash,
        "email": "juan.perez@gmail.com",
        "status": "active",
        "role": "admin",
        "location": {"latitude": 45.04, "longitude": -75.00},
    },)
    
    user = users_repository.get_user(str(uuid_1))

    assert isinstance(user, User)
    assert user.uuid == str(uuid_1)
    assert user.name == 'Juan'


def test_get_user_with_email(users_repository, mock_db_connection_and_cursor, uuid_1, password_hash):
    _, mock_cursor = mock_db_connection_and_cursor
    mock_cursor.fetchone.return_value = ({
        "uuid": str(uuid_1),
        "name": "Juan",
        "surname": "Perez",
        "password": password_hash,
        "email": "juan.perez@gmail.com",
        "status": "active",
        "role": "admin",
        "location": {"latitude": 45.04, "longitude": -75.00},
    },)

    user = users_repository.get_user_with_email("juan.perez@gmail.com")

    assert isinstance(user, User)
    assert user.email == 'juan.perez@gmail.com'


def test_insert_user(users_repository, mock_db_connection_and_cursor, password_hash):
    _, mock_cursor = mock_db_connection_and_cursor
    password = 'hashed-password'
    params_new_user = {
        'name': 'Juan',
        'surname': 'Perez',
        'password': password,
        'email': 'juan.perez@gmail.com',
        'status': 'active',
        'role': 'admin'
    }

    users_repository.insert_user(params_new_user)

    mock_cursor.execute.assert_called_once_with(
        'INSERT INTO users (name, surname, password, email, status, role, notification) VALUES (%s, %s, %s, %s, %s, %s, %s)',
        params=('Juan', 'Perez', password, 'juan.perez@gmail.com', 'active', 'admin', True)
    )


def test_set_location(users_repository, mock_db_connection_and_cursor, uuid_1):
    _, mock_cursor = mock_db_connection_and_cursor
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


def test_check_email(users_repository, mock_db_connection_and_cursor, uuid_1):
    _, mock_cursor = mock_db_connection_and_cursor
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


def test_delete_user(users_repository, mock_db_connection_and_cursor, uuid_1):
    _, mock_cursor = mock_db_connection_and_cursor
    user_id = uuid_1

    users_repository.delete_users(user_id)

    mock_cursor.execute.assert_called_once_with(
        "DELETE FROM users WHERE uuid = %s",
        params=(str(uuid_1),)
    )

def test_get_active_teachers(users_repository, mock_db_connection_and_cursor, uuid_1, uuid_2):
    _, mock_cursor = mock_db_connection_and_cursor
    mock_cursor.fetchall.return_value = [
        ({
            "uuid": str(uuid_1),
            "name": "Carla",
            "surname": "Gómez",
            "password": "hashed-pass",
            "email": "carla.gomez@gmail.com",
            "status": "active",
            "role": "teacher",
            "location": {"latitude": 40.0, "longitude": -3.7},
        },),
        ({
            "uuid": str(uuid_2),
            "name": "Luis",
            "surname": "Martínez",
            "password": "hashed-pass",
            "email": "luis.martinez@gmail.com",
            "status": "active",
            "role": "teacher",
            "location": {"latitude": 41.4, "longitude": 2.1},
        },),
    ]

    teachers = users_repository.get_active_teachers()

    mock_cursor.execute.assert_called_once()
    assert isinstance(teachers, list)
    assert len(teachers) == 2
    assert all(isinstance(t, User) for t in teachers)
    assert teachers[0].email == "carla.gomez@gmail.com"
    assert teachers[1].location.latitude == 41.4


def test_create_pin(users_repository, mock_db_connection_and_cursor, uuid_1):
    mock_conn, mock_cursor = mock_db_connection_and_cursor

    users_repository.create_pin(uuid_1, "654321", "registration")

    mock_cursor.execute.assert_called_once_with(
        """
        INSERT INTO pins (user_id, pin_code, pin_type)
        VALUES (%s, %s, %s)
        """,
        (str(uuid_1), "654321", "registration")
    )
    mock_conn.commit.assert_called_once()

def test_validate_and_use_pin_success(users_repository, mock_db_connection_and_cursor):
    mock_conn, mock_cursor = mock_db_connection_and_cursor
    mock_cursor.fetchone.return_value = ("some-pin-id",)

    result = users_repository.validate_and_use_pin("user@mail.com", "123456", "recovery")

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert result is True


@patch("infrastructure.persistence.users_repository.generate_password_hash")
def test_update_user_password(mock_hash, users_repository, mock_db_connection_and_cursor):
    mock_conn, mock_cursor = mock_db_connection_and_cursor
    mock_hash.return_value = "hashed-pass"
    mock_cursor.fetchone.return_value = ("user-uuid",)

    result = users_repository.update_user_password("user@mail.com", "newpass123")

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert result is True

def test_invalidate_all_pins(users_repository, mock_db_connection_and_cursor, uuid_1):
    mock_conn, mock_cursor = mock_db_connection_and_cursor

    users_repository.invalidate_all_pins(uuid_1)

    mock_cursor.execute.assert_called_once_with(
        """
        UPDATE pins
        SET used = TRUE
        WHERE user_id = %s
        """,
        (str(uuid_1),)
    )
    mock_conn.commit.assert_called_once()

def test_activate_user(users_repository, mock_db_connection_and_cursor):
    mock_conn, mock_cursor = mock_db_connection_and_cursor
    mock_cursor.fetchone.return_value = ("user-uuid",)

    result = users_repository.activate_user("user@mail.com")

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert result is True

def test_update_status(users_repository, mock_db_connection_and_cursor, uuid_1):
    mock_conn, mock_cursor = mock_db_connection_and_cursor
    mock_cursor.fetchone.return_value = (str(uuid_1),)

    result = users_repository.update_status(uuid_1, "inactive")

    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    assert result is True

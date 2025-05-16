import os
from infrastructure.config.db_config import DatabaseConfig
from unittest.mock import patch


def test_database_config_connection_string():
    fake_env = {
        "DB_NAME": "test_db",
        "DB_USER": "test_user",
        "DB_HOST": "localhost",
        "DB_PASSWORD": "test_pass",
        "DB_PORT": "5432"
    }

    with patch.dict(os.environ, fake_env):
        config = DatabaseConfig()
        conn_str = config.connection_strings

        expected = (
            "dbname=test_db user=test_user host=localhost "
            "password=test_pass port=5432"
        )

        assert conn_str == expected

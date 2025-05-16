import pytest
from unittest.mock import patch, MagicMock
import psycopg

from infrastructure.persistence.base_entity import BaseEntity


@patch("infrastructure.persistence.base_entity.psycopg.connect")
@patch("infrastructure.persistence.base_entity.DatabaseConfig")
def test_init_success(mock_config_class, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_config = MagicMock()
    mock_config.connection_strings = "fake-db-url"
    mock_config_class.return_value = mock_config

    entity = BaseEntity()

    mock_connect.assert_called_once_with("fake-db-url")
    assert entity.conn == mock_conn
    assert entity.cursor == mock_cursor


@patch("infrastructure.persistence.base_entity.psycopg.connect", side_effect=psycopg.OperationalError("Connection failed"))
@patch("infrastructure.persistence.base_entity.DatabaseConfig")
def test_connect_with_retries_failure(mock_config_class, mock_connect):
    mock_config = MagicMock()
    mock_config.connection_strings = "fake-db-url"
    mock_config_class.return_value = mock_config

    with pytest.raises(RuntimeError, match="Database connection error."):
        BaseEntity()


@patch("infrastructure.persistence.base_entity.psycopg.connect")
@patch("infrastructure.persistence.base_entity.DatabaseConfig")
def test_commit_calls_cursor_commit(mock_config_class, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_config = MagicMock()
    mock_config.connection_strings = "fake-db-url"
    mock_config_class.return_value = mock_config

    entity = BaseEntity()
    entity.commit()

    mock_cursor.commit.assert_called_once()


@patch("infrastructure.persistence.base_entity.psycopg.connect")
@patch("infrastructure.persistence.base_entity.DatabaseConfig")
def test_del_closes_resources(mock_config_class, mock_connect):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_connect.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    mock_config = MagicMock()
    mock_config.connection_strings = "fake-db-url"
    mock_config_class.return_value = mock_config

    entity = BaseEntity()
    del entity  # trigger __del__

    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

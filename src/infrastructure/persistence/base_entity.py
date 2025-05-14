import psycopg
import time
from flask import current_app

from infrastructure.config.db_config import DatabaseConfig


class BaseEntity:

    def __init__(self):
        self.conn = self.connect_with_retries()
        self.cursor = self.conn.cursor()

    def connect_with_retries(self, retries=5, delay=3):
        """Retry connecting to the DB until it is available."""
        for attempt in range(retries):
            try:
                connection_string = DatabaseConfig().connection_strings
                return psycopg.connect(connection_string)
            except psycopg.OperationalError:
                time.sleep(delay)
        current_app.logger.error("Users API - Database connection error.")
        raise RuntimeError("Database connection error.")

    def commit(self):
        self.cursor.commit()

    def __del__(self):
        if hasattr(self, "cursor"):
            self.cursor.close()
        if hasattr(self, "conn"):
            self.conn.close()

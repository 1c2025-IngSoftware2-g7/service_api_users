import psycopg
import time
from src.infrastructure.config.db_config import DatabaseConfig

class BaseEntity:

    def __init__(self):
        self.conn = self.connect_with_retries()
        self.cursor = self.conn.cursor()

    """Retry connecting to the DB until it is available."""
    def connect_with_retries(self, retries=5, delay=3):
        for attempt in range(retries):
            try:
                connection_string = DatabaseConfig().connection_strings
                return psycopg.connect(connection_string)
            except psycopg.OperationalError:
                time.sleep(delay)
        raise RuntimeError("Database connection error.")

        
    def commit(self):
        self.cursor.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

import psycopg
from src.infrastructure.config.db_config import DatabaseConfig

class BaseEntity:
    # instance = None

    # def __new__(cls, *args, **kwargs):
    #     if cls.instance is None:
    #         cls.instance = super().__new__(BaseEntity)
    #         return cls.instance
    #     return cls.instance

    def __init__(self):
        self.conn = self.connect()
        self.cursor = self.conn.cursor()

    def connect(self):
        try:
            db_config = DatabaseConfig()
            connection_strings = db_config.connection_strings
            return psycopg.connect(connection_strings)
        except psycopg.Error as e:
            raise RuntimeError("Database connection error.")
        
    def commit(self):
        self.cursor.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

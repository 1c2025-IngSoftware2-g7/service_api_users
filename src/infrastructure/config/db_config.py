import os

class DatabaseConfig:
    host: str
    database: str
    user: str
    password: str

    def __init__(self):
        self.database = os.getenv("DATABASE_NAME")
        self.user = os.getenv("DATABASE_USER")
        self.host = os.getenv("DATABASE_HOST")
        self.password = os.getenv("DATABASE_PASSWORD")

    @property
    def connection_strings(self) -> str:
        return f"dbname={self.database} user={self.user} host={self.host} password={self.password}"

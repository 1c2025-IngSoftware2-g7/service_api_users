import psycopg

class BaseEntity:
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(BaseEntity)
            return cls.instance
        return cls.instance

    def __init__(self, db_name, user, password, host):
        self.name = db_name
        self.conn = self.connect(db_name, user, password, host)
        self.cursor = self.conn.cursor()

    def connect(self, db_name, user, password, host):
        try:
            return psycopg.connect(
                f"dbname={db_name} user={user} host={host} password={password}"
            )
        except psycopg.Error as e:
            raise RuntimeError("Database connection error.")
        
    def commit(self):
        self.cursor.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

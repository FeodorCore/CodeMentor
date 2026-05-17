import sqlite3
from contextlib import contextmanager
from config import DB_PATH

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # чтобы возвращать словари
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute(self, query: str, params: tuple = ()):
        with self.connect() as conn:
            cursor = conn.execute(query, params)
            return cursor

    def fetch_one(self, query: str, params: tuple = ()):
        with self.connect() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchone()

    def fetch_all(self, query: str, params: tuple = ()):
        with self.connect() as conn:
            cursor = conn.execute(query, params)
            return cursor.fetchall()

# глобальный экземпляр
db = Database()
import sqlite3
import os
from typing import NoReturn

class DatabaseManager:
    def __init__(self, db_name: str = "app.db", schema_name: str = "schema.sql") -> None:
        self.db_name: str = db_name
        self.schema_name: str = schema_name

    def init_db(self) -> None:
        if os.path.exists(self.db_name):
            print(f"Database file '{self.db_name}' already exists. Deleting...")
            os.remove(self.db_name)
        self._create_table()
        print("Database successfully reinitialized and tables created.")

    def create_or_skip(self) -> None:
        if os.path.exists(self.db_name):
            print(f"Database file '{self.db_name}' already exists. Skipping initialization.")
            return
        self._create_table()
        print("Database successfully created.")

    def _create_table(self) -> None | NoReturn:
        conn: sqlite3.Connection = sqlite3.connect(self.db_name)
        try:
            with open(self.schema_name, 'r', encoding='utf-8') as f:
                sql_script: str = f.read()
            conn.execute("PRAGMA foreign_keys = ON;")

            conn.executescript(sql_script)
            conn.commit()
        except Exception as e:
            print(f"Error during database creation: {e}")
            raise e
        finally:
            conn.close()


if __name__ == "__main__":
    db = DatabaseManager()
    db.create_or_skip()
    # db.init_db()
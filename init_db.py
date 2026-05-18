# init_db.py
import sqlite3
import os


class DatabaseManager:
    def __init__(self, db_name="app.db", schema_name="schema.sql"):
        self.db_name = db_name
        self.schema_name = schema_name

    def init_db(self):
        if os.path.exists(self.db_name):
            print(f"Удаление старой базы данных '{self.db_name}'...")
            os.remove(self.db_name)
        self._create_table()
        print("База данных успешно инициализирована с новой схемой.")

    def create_or_skip(self):
        if os.path.exists(self.db_name):
            print(f"База данных '{self.db_name}' уже существует. Пропускаем создание.")
            return
        self._create_table()
        print("База данных создана впервые.")

    def _create_table(self):
        conn = sqlite3.connect(self.db_name)
        try:
            with open(self.schema_name, 'r', encoding='utf-8') as f:
                sql_script = f.read()
            conn.execute("PRAGMA foreign_keys = ON;")

            conn.executescript(sql_script)
            conn.commit()
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            raise e
        finally:
            conn.close()


if __name__ == "__main__":
    db = DatabaseManager()
    db.create_or_skip()
    # db.init_db()
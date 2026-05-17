import sqlite3
from config import DB_PATH


def init_database():
    with open("create_db.sql", "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(sql_script)
    conn.close()
    print("База данных успешно создана")


if __name__ == "__main__":
    init_database()
import sqlite3
from app.models.users import UserResponse, UserProgressResponse

class UserService:
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_all(self) -> list[UserResponse]:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, telegram_id, is_admin FROM User ORDER BY id ASC")
            return [UserResponse(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_by_id(self, user_id: int) -> UserResponse | None:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, telegram_id, is_admin FROM User WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return UserResponse(**dict(row)) if row else None
        finally:
            conn.close()


class UserProgressService:
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_by_user(self, user_id: int, category_id: int | None = None) -> list[UserProgressResponse]:
        """Получить прогресс пользователя с JOIN на уроки и категории."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            query = """
                SELECT up.id, up.user_id, up.lesson_id, up.learned, up.completed_at,
                       l.title as lesson_title, l.category_id, c.name as category_name
                FROM UserProgress up
                JOIN Lesson l ON up.lesson_id = l.id
                JOIN Category c ON l.category_id = c.id
                WHERE up.user_id = ?
            """
            params = [user_id]
            if category_id is not None:
                query += " AND l.category_id = ?"
                params.append(category_id)
            query += " ORDER BY c.id ASC, l.sort_order ASC"

            cursor.execute(query, params)
            return [UserProgressResponse(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()
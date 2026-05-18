import sqlite3
from app.models.lessons import LessonCreate, LessonResponse

class LessonService:
    """Сервис для работы с уроками (статьями)."""
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        """Внутренний метод для получения соединения."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_by_category(self, category_id: int) -> list[LessonResponse]:
        """Получить все уроки из конкретной категории с сортировкой."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, category_id, sort_order, title, content "
                "FROM Lesson WHERE category_id = ? ORDER BY sort_order ASC, id ASC",
                (category_id,)
            )
            rows = cursor.fetchall()
            return [LessonResponse(**dict(row)) for row in rows]
        finally:
            conn.close()

    def create(self, lesson_data: LessonCreate) -> LessonResponse:
        """Создать новый урок."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Lesson (category_id, sort_order, title, content) VALUES (?, ?, ?, ?)",
                (lesson_data.category_id, lesson_data.sort_order, lesson_data.title, lesson_data.content)
            )
            conn.commit()
            new_id = cursor.lastrowid
            return LessonResponse(
                id=new_id,
                category_id=lesson_data.category_id,
                sort_order=lesson_data.sort_order,
                title=lesson_data.title,
                content=lesson_data.content
            )
        except sqlite3.IntegrityError:
            # Сработает, если передан несуществующий category_id (благодаря FOREIGN KEY)
            raise ValueError(f"Категория с ID {lesson_data.category_id} не существует.")
        finally:
            conn.close()

    def delete(self, lesson_id: int) -> bool:
        """Удалить урок по ID."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM Lesson WHERE id = ?", (lesson_id,))
            if not cursor.fetchone():
                return False

            cursor.execute("DELETE FROM Lesson WHERE id = ?", (lesson_id,))
            conn.commit()
            return True
        finally:
            conn.close()
# app/services/lessons.py
import sqlite3
from app.models.lessons import LessonCreate, LessonUpdate, LessonResponse


class LessonService:
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_all(self) -> list[LessonResponse]:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, category_id, sort_order, title, content "
                "FROM Lesson ORDER BY category_id ASC, sort_order ASC"
            )
            return [LessonResponse(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

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
            return [LessonResponse(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_by_id(self, lesson_id: int) -> LessonResponse | None:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, category_id, sort_order, title, content FROM Lesson WHERE id = ?",
                (lesson_id,)
            )
            row = cursor.fetchone()
            return LessonResponse(**dict(row)) if row else None
        finally:
            conn.close()

    def create(self, lesson_data: LessonCreate) -> LessonResponse:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # 1. Сдвигаем существующие уроки вниз (>= N становятся N+1)
            cursor.execute(
                "UPDATE Lesson SET sort_order = sort_order + 1 "
                "WHERE category_id = ? AND sort_order >= ?",
                (lesson_data.category_id, lesson_data.sort_order)
            )
            # 2. Вставляем новый урок
            cursor.execute(
                "INSERT INTO Lesson (category_id, sort_order, title, content) VALUES (?, ?, ?, ?)",
                (lesson_data.category_id, lesson_data.sort_order, lesson_data.title, lesson_data.content)
            )
            conn.commit()
            return LessonResponse(
                id=cursor.lastrowid,
                category_id=lesson_data.category_id,
                sort_order=lesson_data.sort_order,
                title=lesson_data.title,
                content=lesson_data.content
            )
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Ошибка целостности БД: {e}")
        finally:
            conn.close()

    def update(self, lesson_id: int, lesson_data: LessonUpdate) -> LessonResponse:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # Получаем старые данные в рамках транзакции
            cursor.execute("SELECT id, category_id, sort_order, title, content FROM Lesson WHERE id = ?", (lesson_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Урок с ID {lesson_id} не найден.")
            old_lesson = LessonResponse(**dict(row))

            if lesson_data.sort_order < 1:
                raise ValueError("Позиция (sort_order) должна быть >= 1.")

            # Если изменилась категория или позиция — пересчитываем порядок
            if old_lesson.category_id != lesson_data.category_id or old_lesson.sort_order != lesson_data.sort_order:
                old_cat, old_pos = old_lesson.category_id, old_lesson.sort_order
                new_cat, new_pos = lesson_data.category_id, lesson_data.sort_order

                if old_cat == new_cat:
                    # Перемещение внутри одной категории
                    if new_pos < old_pos:
                        cursor.execute(
                            "UPDATE Lesson SET sort_order = sort_order + 1 "
                            "WHERE category_id = ? AND sort_order >= ? AND sort_order < ?",
                            (new_cat, new_pos, old_pos)
                        )
                    elif new_pos > old_pos:
                        cursor.execute(
                            "UPDATE Lesson SET sort_order = sort_order - 1 "
                            "WHERE category_id = ? AND sort_order > ? AND sort_order <= ?",
                            (new_cat, old_pos, new_pos)
                        )
                else:
                    # Перенос в другую категорию
                    cursor.execute(
                        "UPDATE Lesson SET sort_order = sort_order - 1 "
                        "WHERE category_id = ? AND sort_order > ?",
                        (old_cat, old_pos)
                    )
                    cursor.execute(
                        "UPDATE Lesson SET sort_order = sort_order + 1 "
                        "WHERE category_id = ? AND sort_order >= ?",
                        (new_cat, new_pos)
                    )

            # Обновляем сам урок
            cursor.execute(
                "UPDATE Lesson SET category_id = ?, sort_order = ?, title = ?, content = ? WHERE id = ?",
                (lesson_data.category_id, lesson_data.sort_order, lesson_data.title, lesson_data.content, lesson_id)
            )
            conn.commit()
            return LessonResponse(
                id=lesson_id,
                category_id=lesson_data.category_id,
                sort_order=lesson_data.sort_order,
                title=lesson_data.title,
                content=lesson_data.content
            )
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Ошибка целостности БД: {e}")
        finally:
            conn.close()

    def delete(self, lesson_id: int) -> bool:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            lesson = self.get_by_id(lesson_id)
            if not lesson:
                return False

            cursor.execute("DELETE FROM Lesson WHERE id = ?", (lesson_id,))
            cursor.execute(
                "UPDATE Lesson SET sort_order = sort_order - 1 "
                "WHERE category_id = ? AND sort_order > ?",
                (lesson.category_id, lesson.sort_order)
            )
            conn.commit()
            return True
        finally:
            conn.close()
# app/services/categories.py
import sqlite3
from app.models.categories import CategoryCreate, CategoryUpdate, CategoryResponse


class CategoryService:
    """Сервис для работы с категориями."""

    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_all(self) -> list[CategoryResponse]:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM Category ORDER BY id ASC")
            rows = cursor.fetchall()
            return [CategoryResponse(**dict(row)) for row in rows]
        finally:
            conn.close()

    def get_by_id(self, category_id: int) -> CategoryResponse | None:
        """Получить категорию по ID."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM Category WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            return CategoryResponse(**dict(row)) if row else None
        finally:
            conn.close()

    def create(self, category_data: CategoryCreate) -> CategoryResponse:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Category (name) VALUES (?)", (category_data.name,))
            conn.commit()
            return CategoryResponse(id=cursor.lastrowid, name=category_data.name)
        except sqlite3.IntegrityError:
            raise ValueError(f"Категория '{category_data.name}' уже существует.")
        finally:
            conn.close()

    def update(self, category_id: int, category_data: CategoryUpdate) -> CategoryResponse:
        """Обновить название категории."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            if not self.get_by_id(category_id):
                raise ValueError(f"Категория с ID {category_id} не найдена.")

            cursor.execute("UPDATE Category SET name = ? WHERE id = ?", (category_data.name, category_id))
            conn.commit()
            return CategoryResponse(id=category_id, name=category_data.name)
        except sqlite3.IntegrityError:
            raise ValueError(f"Категория '{category_data.name}' уже существует.")
        finally:
            conn.close()

    def delete(self, category_id: int) -> bool:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            if not self.get_by_id(category_id):
                return False
            cursor.execute("DELETE FROM Category WHERE id = ?", (category_id,))
            conn.commit()
            return True
        finally:
            conn.close()
import sqlite3
from app.models.categories import CategoryCreate, CategoryResponse

class CategoryService:
    """Сервис для работы с категориями."""
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        """Внутренний метод для получения соединения."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_all(self) -> list[CategoryResponse]:
        """Получить все категории."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM Category ORDER BY id ASC")
            rows = cursor.fetchall()
            return [CategoryResponse(**dict(row)) for row in rows]
        finally:
            conn.close()

    def create(self, category_data: CategoryCreate) -> CategoryResponse:
        """Создать новую категорию."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Category (name) VALUES (?)",
                (category_data.name,)
            )
            conn.commit()
            new_id = cursor.lastrowid
            return CategoryResponse(id=new_id, name=category_data.name)
        except sqlite3.IntegrityError:
            raise ValueError(f"Категория '{category_data.name}' уже существует.")
        finally:
            conn.close()

    def delete(self, category_id: int) -> bool:
        """Удалить категорию по ID."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # Проверяем существование
            cursor.execute("SELECT id FROM Category WHERE id = ?", (category_id,))
            if not cursor.fetchone():
                return False

            cursor.execute("DELETE FROM Category WHERE id = ?", (category_id,))
            conn.commit()
            return True
        finally:
            conn.close()
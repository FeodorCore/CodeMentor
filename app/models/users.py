from pydantic import BaseModel
from typing import Optional

class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    is_admin: bool

class UserProgressResponse(BaseModel):
    id: int
    user_id: int
    lesson_id: int
    learned: bool
    completed_at: Optional[str] = None
    # Поля из связанных таблиц для удобного вывода
    lesson_title: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
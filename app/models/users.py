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
    lesson_title: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None


class UserSync(BaseModel):
    telegram_id: int
    username: Optional[str] = None


class ProgressUpdate(BaseModel):
    lesson_id: int


# === НОВЫЕ МОДЕЛИ ДЛЯ ДЕТАЛЬНОГО ПРОГРЕССА ===
class UserAnswerDetail(BaseModel):
    id: int
    question_text: str
    user_answer_text: str
    correct_answer_text: Optional[str] = None
    is_correct: bool
    answered_at: Optional[str] = None


class LessonProgressDetail(BaseModel):
    lesson_id: int
    lesson_title: str
    sort_order: int
    category_id: int
    category_name: str
    learned: bool
    completed_at: Optional[str] = None
    answers: list[UserAnswerDetail] = []


from fastapi import APIRouter, HTTPException
from app.services.categories import CategoryService
from app.services.lessons import LessonService
from app.models.categories import CategoryResponse
from app.models.lessons import LessonResponse

router = APIRouter()
category_service = CategoryService()
lesson_service = LessonService()

@router.get("/categories", response_model=list[CategoryResponse])
def get_bot_categories():
    """Получить все категории для главного меню бота."""
    return category_service.get_all()

@router.get("/categories/{category_id}/lessons", response_model=list[LessonResponse])
def get_bot_lessons(category_id: int):
    """Получить список уроков в категории."""
    return lesson_service.get_by_category(category_id)

@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_bot_lesson_content(lesson_id: int):
    """Получить текст конкретного урока для отправки в Telegram."""
    lesson = lesson_service.get_by_id(lesson_id)
    if not lesson:
        raise HTTPException(status_code=404, detail="Урок не найден")
    return lesson
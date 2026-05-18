from fastapi import APIRouter, HTTPException
from app.services.lessons import LessonService
from app.models.lessons import LessonCreate, LessonResponse

lesson_service = LessonService()
router = APIRouter()

@router.get("/categories/{category_id}/lessons", response_model=list[LessonResponse])
def get_lessons_by_category(category_id: int):
    """Получить список всех уроков в категории."""
    try:
        return lesson_service.get_by_category(category_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lessons", response_model=LessonResponse, status_code=201)
def create_lesson(lesson: LessonCreate):
    """Создать новый урок."""
    try:
        return lesson_service.create(lesson)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/lessons/{lesson_id}", status_code=204)
def delete_lesson(lesson_id: int):
    """Удалить урок по ID."""
    try:
        success = lesson_service.delete(lesson_id)
        if not success:
            raise HTTPException(status_code=404, detail="Урок не найден")
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
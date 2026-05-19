from fastapi import APIRouter, HTTPException
from app.services.users import UserService, UserProgressService
from app.models.users import UserSync, ProgressUpdate, UserResponse

router = APIRouter()
user_service = UserService()
progress_service = UserProgressService()


@router.post("/users/sync", response_model=UserResponse)
def sync_bot_user(user_data: UserSync):
    """Синхронизация пользователя (вызывается при /start в боте)."""
    try:
        return user_service.sync_user(user_data.telegram_id, user_data.username)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{telegram_id}", response_model=UserResponse)
def get_bot_user(telegram_id: int):
    """Получить профиль пользователя по Telegram ID."""
    user = user_service.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден. Сначала вызовите /sync")
    return user


@router.post("/users/{telegram_id}/progress")
def update_progress(telegram_id: int, progress: ProgressUpdate):
    """Сохранить прогресс (когда пользователь прочитал урок)."""
    user = user_service.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    try:
        progress_service.mark_completed(user.id, progress.lesson_id)
        return {"status": "success", "message": "Урок отмечен как пройденный"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users/{telegram_id}/next-lesson")
def get_next_lesson(telegram_id: int, category_id: int):
    """Получить ID следующего урока для кнопки 'Продолжить'."""
    user = user_service.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    next_lesson_id = progress_service.get_next_lesson_id(user.id, category_id)
    return {"next_lesson_id": next_lesson_id}
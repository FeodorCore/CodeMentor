from fastapi import APIRouter, HTTPException
from app.services.questions import QuestionService
from app.services.users import UserService
from app.models.questions import QuestionResponse
from pydantic import BaseModel
import sqlite3

router = APIRouter()
question_service = QuestionService()
user_service = UserService()


class AnswerSubmit(BaseModel):
    telegram_id: int
    answer_option_id: int
    is_correct: bool


@router.get("/lessons/{lesson_id}/questions", response_model=list[QuestionResponse])
def get_lesson_questions(lesson_id: int):
    """Получить вопросы и варианты ответов для урока."""
    return question_service.get_by_lesson(lesson_id)


@router.post("/users/answers")
def submit_user_answer(data: AnswerSubmit):
    """Сохранить ответ пользователя (правильный или нет)."""
    user = user_service.get_by_telegram_id(data.telegram_id)
    if not user:
        raise HTTPException(404, detail="Пользователь не найден")

    conn = sqlite3.connect("app.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        conn.execute(
            "INSERT INTO UserAnswer (user_id, answer_option_id, is_correct) VALUES (?, ?, ?)",
            (user.id, data.answer_option_id, data.is_correct),
        )
        conn.commit()
        return {"status": "saved", "is_correct": data.is_correct}
    except Exception as e:
        raise HTTPException(500, detail=str(e))
    finally:
        conn.close()

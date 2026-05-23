from pydantic import BaseModel
from typing import Optional


class AnswerOptionCreate(BaseModel):
    text: str
    is_correct: bool = False
    sort_order: int = 0


class AnswerOptionResponse(BaseModel):
    id: int
    question_id: int
    text: str
    is_correct: bool
    sort_order: int


class QuestionCreate(BaseModel):
    text: str
    sort_order: int = 0
    answers: list[AnswerOptionCreate] = []


class QuestionResponse(BaseModel):
    id: int
    lesson_id: int
    text: str
    sort_order: int
    answers: list[AnswerOptionResponse] = []


class QuestionUpdate(BaseModel):
    """Для обновления вопросов целиком (пересоздание)."""

    questions: list[QuestionCreate] = []

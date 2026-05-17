from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from crud import (
    get_user_by_tg_id,
    get_answers_by_question,
    save_user_answer
)
from auth import verify_api_key

router = APIRouter(prefix="/quiz", tags=["quiz"])


class CheckAnswerRequest(BaseModel):
    tg_id: int
    question_id: int
    answer_id: int


@router.post("/check", dependencies=[Depends(verify_api_key)])
def check_answer(req: CheckAnswerRequest):
    user = get_user_by_tg_id(req.tg_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # проверим, что answer принадлежит question
    answers = get_answers_by_question(req.question_id)
    answer_ids = [a["id"] for a in answers]
    if req.answer_id not in answer_ids:
        raise HTTPException(status_code=400, detail="Answer does not belong to question")

    # найдём правильный ответ
    correct_answer = next((a for a in answers if a["is_correct"]), None)
    is_right = (correct_answer and correct_answer["id"] == req.answer_id)

    # сохраняем историю
    save_user_answer(user["id"], req.question_id, req.answer_id, is_right)

    return {
        "correct": is_right,
        "explanation": "Верно!" if is_right else "Неправильно. Попробуйте ещё раз."
    }
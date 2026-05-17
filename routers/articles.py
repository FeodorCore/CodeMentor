from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from crud import (
    get_all_articles, get_article, get_questions_by_article, get_answers_by_question
)
from auth import verify_api_key

router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("/", dependencies=[Depends(verify_api_key)])
def list_articles() -> List[Dict[str, Any]]:
    """Список всех статей (без содержимого)"""
    articles = get_all_articles()
    # убираем content для краткости
    for a in articles:
        a.pop("content", None)
    return articles


@router.get("/{article_id}", dependencies=[Depends(verify_api_key)])
def get_article_by_id(article_id: int) -> Dict[str, Any]:
    """Полная статья с содержимым"""
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/{article_id}/quiz", dependencies=[Depends(verify_api_key)])
def get_quiz_for_article(article_id: int) -> Dict[str, Any]:
    """Возвращает вопросы и варианты ответов (без флага правильности)"""
    article = get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    questions = get_questions_by_article(article_id)
    result = {
        "article_id": article_id,
        "title": article["title"],
        "questions": []
    }
    for q in questions:
        answers = get_answers_by_question(q["id"])
        # убираем is_correct
        safe_answers = [{"id": a["id"], "text": a["text"]} for a in answers]
        result["questions"].append({
            "id": q["id"],
            "text": q["text"],
            "answers": safe_answers
        })
    return result
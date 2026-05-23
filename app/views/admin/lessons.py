import json
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.services.lessons import LessonService
from app.services.categories import CategoryService
from app.services.questions import QuestionService
from app.models.lessons import LessonCreate, LessonUpdate
from app.models.questions import QuestionCreate, AnswerOptionCreate
from app.views.admin import templates

router = APIRouter()
lesson_service = LessonService()
category_service = CategoryService()
question_service = QuestionService()


def _parse_questions_json(questions_json: str) -> list[QuestionCreate]:
    """Строгая валидация: ровно 1 вопрос, минимум 2 ответа, минимум 1 правильный."""
    if not questions_json or questions_json.strip() in ("", "[]", "null"):
        raise ValueError("Урок должен содержать ровно 1 вопрос.")
    try:
        data = json.loads(questions_json)
    except json.JSONDecodeError:
        raise ValueError("Некорректный формат данных вопросов (JSON)")

    if not isinstance(data, list) or len(data) != 1:
        raise ValueError("Урок должен содержать ровно 1 вопрос.")

    q_data = data[0]
    text = q_data.get("text", "").strip()
    if not text:
        raise ValueError("Текст вопроса не может быть пустым.")

    answers_raw = q_data.get("answers", [])
    if len(answers_raw) < 2:
        raise ValueError("Вопрос должен содержать минимум 2 варианта ответа.")

    answers = []
    for a_idx, a_data in enumerate(answers_raw):
        a_text = a_data.get("text", "").strip()
        if not a_text:
            raise ValueError(f"Вариант ответа {a_idx + 1} не может быть пустым.")
        answers.append(
            AnswerOptionCreate(
                text=a_text,
                is_correct=bool(a_data.get("is_correct", False)),
                sort_order=a_idx,
            )
        )

    if not any(a.is_correct for a in answers):
        raise ValueError("В вопросе не отмечен правильный ответ.")

    return [QuestionCreate(text=text, sort_order=0, answers=answers)]


@router.get("/lessons")
async def lessons_page(request: Request):
    category_id_str = request.query_params.get("category_id")
    categories = category_service.get_all()
    if category_id_str and category_id_str.isdigit():
        category_id = int(category_id_str)
        lessons = lesson_service.get_by_category(category_id)
        selected_category_id = category_id
    else:
        lessons = lesson_service.get_all()
        selected_category_id = None

    cat_map = {c.id: c.name for c in categories}
    error = request.query_params.get("error")
    success = request.query_params.get("success")

    return templates.TemplateResponse(
        request=request,
        name="lessons.html",
        context={
            "lessons": lessons,
            "categories": categories,
            "cat_map": cat_map,
            "selected_category_id": selected_category_id,
            "error": error,
            "success": success,
        },
    )


@router.get("/lessons/create")
async def create_lesson_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="edit_lesson.html",
        context={
            "lesson": None,
            "categories": category_service.get_all(),
            "error": None,
            "form_data": {},
            "initial_questions": [],
        },
    )


@router.post("/lessons")
async def create_lesson(
    request: Request,
    category_id: int = Form(...),
    sort_order: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    questions_json: str = Form(""),
):
    # 1. Валидация ДО создания урока
    try:
        questions = _parse_questions_json(questions_json)
    except ValueError as e:
        try:
            initial_q = json.loads(questions_json) if questions_json else []
        except Exception:
            initial_q = []
        return templates.TemplateResponse(
            request=request,
            name="edit_lesson.html",
            context={
                "lesson": None,
                "categories": category_service.get_all(),
                "error": str(e),
                "form_data": {
                    "category_id": category_id,
                    "sort_order": sort_order,
                    "title": title,
                    "content": content,
                },
                "initial_questions": initial_q,
            },
            status_code=400,
        )

    # 2. Создаём урок и вопросы только если валидно
    try:
        lesson = lesson_service.create(
            LessonCreate(
                category_id=category_id,
                sort_order=sort_order,
                title=title,
                content=content,
            )
        )
        question_service.replace_questions_for_lesson(lesson.id, questions)
        return RedirectResponse(url="/admin/ui/lessons?success=1", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="edit_lesson.html",
            context={
                "lesson": None,
                "categories": category_service.get_all(),
                "error": f"Ошибка сервера: {e}",
                "form_data": {
                    "category_id": category_id,
                    "sort_order": sort_order,
                    "title": title,
                    "content": content,
                },
                "initial_questions": json.loads(questions_json)
                if questions_json
                else [],
            },
            status_code=500,
        )


@router.get("/lessons/{lesson_id}/edit")
async def edit_lesson_page(request: Request, lesson_id: int):
    lesson = lesson_service.get_by_id(lesson_id)
    if not lesson:
        return RedirectResponse(url="/admin/ui/lessons", status_code=303)

    questions = question_service.get_by_lesson(lesson_id)
    initial_questions = [q.model_dump() for q in questions]

    return templates.TemplateResponse(
        request=request,
        name="edit_lesson.html",
        context={
            "lesson": lesson,
            "categories": category_service.get_all(),
            "error": request.query_params.get("error"),
            "form_data": {},
            "initial_questions": initial_questions,
        },
    )


@router.post("/lessons/{lesson_id}/edit")
async def update_lesson(
    request: Request,
    lesson_id: int,
    category_id: int = Form(...),
    sort_order: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    questions_json: str = Form(""),
):
    # 1. Валидация ДО обновления
    try:
        questions = _parse_questions_json(questions_json)
    except ValueError as e:
        try:
            initial_q = json.loads(questions_json) if questions_json else []
        except Exception:
            initial_q = []
        return templates.TemplateResponse(
            request=request,
            name="edit_lesson.html",
            context={
                "lesson": lesson_service.get_by_id(lesson_id),
                "categories": category_service.get_all(),
                "error": str(e),
                "form_data": {
                    "category_id": category_id,
                    "sort_order": sort_order,
                    "title": title,
                    "content": content,
                },
                "initial_questions": initial_q,
            },
            status_code=400,
        )

    # 2. Обновляем только если валидно
    try:
        lesson_service.update(
            lesson_id,
            LessonUpdate(
                category_id=category_id,
                sort_order=sort_order,
                title=title,
                content=content,
            ),
        )
        question_service.replace_questions_for_lesson(lesson_id, questions)
        return RedirectResponse(url="/admin/ui/lessons?success=1", status_code=303)
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="edit_lesson.html",
            context={
                "lesson": lesson_service.get_by_id(lesson_id),
                "categories": category_service.get_all(),
                "error": f"Ошибка сервера: {e}",
                "form_data": {
                    "category_id": category_id,
                    "sort_order": sort_order,
                    "title": title,
                    "content": content,
                },
                "initial_questions": json.loads(questions_json)
                if questions_json
                else [],
            },
            status_code=500,
        )


@router.post("/lessons/{lesson_id}/delete")
async def delete_lesson(lesson_id: int):
    lesson_service.delete(lesson_id)
    return RedirectResponse(url="/admin/ui/lessons", status_code=303)

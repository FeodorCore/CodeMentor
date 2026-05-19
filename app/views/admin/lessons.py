# app/views/admin/lessons.py
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from app.services.lessons import LessonService
from app.services.categories import CategoryService
from app.models.lessons import LessonCreate, LessonUpdate
from app.views.admin import templates

router = APIRouter()
lesson_service = LessonService()
category_service = CategoryService()

@router.get("/lessons")
async def lessons_page(request: Request):
    category_id_str = request.query_params.get("category_id")
    categories = category_service.get_all()

    # Если выбрана конкретная категория — фильтруем, иначе грузим всё
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
            "success": success
        }
    )

@router.get("/lessons/create")
async def create_lesson_page(request: Request):
    categories = category_service.get_all()
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request=request,
        name="edit_lesson.html",
        context={"lesson": None, "categories": categories, "error": error}
    )

@router.post("/lessons")
async def create_lesson(
    category_id: int = Form(...),
    sort_order: int = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    try:
        lesson_service.create(LessonCreate(
            category_id=category_id, sort_order=sort_order, title=title, content=content
        ))
        return RedirectResponse(url="/admin/ui/lessons?success=1", status_code=303)
    except ValueError as e:
        return RedirectResponse(url=f"/admin/ui/lessons/create?error={e}", status_code=303)

@router.get("/lessons/{lesson_id}/edit")
async def edit_lesson_page(request: Request, lesson_id: int):
    lesson = lesson_service.get_by_id(lesson_id)
    if not lesson:
        return RedirectResponse(url="/admin/ui/lessons", status_code=303)
    categories = category_service.get_all()
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request=request,
        name="edit_lesson.html",
        context={"lesson": lesson, "categories": categories, "error": error}
    )

@router.post("/lessons/{lesson_id}/edit")
async def update_lesson(
    lesson_id: int,
    category_id: int = Form(...),
    sort_order: int = Form(...),
    title: str = Form(...),
    content: str = Form(...)
):
    try:
        lesson_service.update(lesson_id, LessonUpdate(
            category_id=category_id, sort_order=sort_order, title=title, content=content
        ))
        return RedirectResponse(url="/admin/ui/lessons?success=1", status_code=303)
    except ValueError as e:
        return RedirectResponse(url=f"/admin/ui/lessons/{lesson_id}/edit?error={e}", status_code=303)

@router.post("/lessons/{lesson_id}/delete")
async def delete_lesson(lesson_id: int):
    lesson_service.delete(lesson_id)
    return RedirectResponse(url="/admin/ui/lessons", status_code=303)
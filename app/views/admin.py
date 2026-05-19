# app/views/admin.py
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.categories import CategoryService
from app.models.categories import CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/admin/ui", tags=["Admin Web UI"])

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

category_service = CategoryService()

@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})

@router.get("/categories")
async def categories_page(request: Request):
    categories = category_service.get_all()
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request=request,
        name="categories.html",
        context={"categories": categories, "error": error}
    )

@router.post("/categories")
async def create_category(name: str = Form(...)):
    try:
        category_service.create(CategoryCreate(name=name))
        return RedirectResponse(url="/admin/ui/categories", status_code=303)
    except ValueError as e:
        return RedirectResponse(url=f"/admin/ui/categories?error={e}", status_code=303)

@router.get("/categories/{category_id}/edit")
async def edit_category_page(request: Request, category_id: int):
    category = category_service.get_by_id(category_id)
    if not category:
        return RedirectResponse(url="/admin/ui/categories", status_code=303)
    error = request.query_params.get("error")
    return templates.TemplateResponse(
        request=request,
        name="edit_category.html",
        context={"category": category, "error": error}
    )

@router.post("/categories/{category_id}/edit")
async def update_category(category_id: int, name: str = Form(...)):
    try:
        category_service.update(category_id, CategoryUpdate(name=name))
        return RedirectResponse(url="/admin/ui/categories", status_code=303)
    except ValueError as e:
        return RedirectResponse(url=f"/admin/ui/categories/{category_id}/edit?error={e}", status_code=303)

@router.post("/categories/{category_id}/delete")
async def delete_category(category_id: int):
    category_service.delete(category_id)
    return RedirectResponse(url="/admin/ui/categories", status_code=303)
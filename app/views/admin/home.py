from fastapi import APIRouter, Request
from app.services.categories import CategoryService
from app.views.admin import templates
router = APIRouter()

category_service = CategoryService()

@router.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})
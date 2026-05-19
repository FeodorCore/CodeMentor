from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from app.services.users import UserService, UserProgressService
from app.services.categories import CategoryService
from app.views.admin import templates

router = APIRouter()
user_service = UserService()
progress_service = UserProgressService()
category_service = CategoryService()

@router.get("/users")
async def users_page(request: Request):
    users = user_service.get_all()
    return templates.TemplateResponse(
        request=request,
        name="users.html",
        context={"users": users}
    )

@router.get("/users/{user_id}/progress")
async def user_progress_page(request: Request, user_id: int):
    user = user_service.get_by_id(user_id)
    if not user:
        return RedirectResponse(url="/admin/ui/users", status_code=303)

    category_id_str = request.query_params.get("category_id")
    categories = category_service.get_all()

    if category_id_str and category_id_str.isdigit():
        category_id = int(category_id_str)
        progress = progress_service.get_by_user(user_id, category_id)
        selected_category_id = category_id
    else:
        progress = progress_service.get_by_user(user_id)
        selected_category_id = None

    return templates.TemplateResponse(
        request=request,
        name="user_progress.html",
        context={
            "user": user,
            "progress": progress,
            "categories": categories,
            "selected_category_id": selected_category_id
        }
    )
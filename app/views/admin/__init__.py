from pathlib import Path
from fastapi import APIRouter
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

from app.views.admin.categories import router as categories_router
from app.views.admin.home import router as home_router
from app.views.admin.lessons import router as lessons_router
from app.views.admin.users import router as users_router  # <-- добавлено

router = APIRouter(prefix="/admin/ui", tags=["Admin Web UI"])
router.include_router(home_router)
router.include_router(categories_router)
router.include_router(lessons_router)
router.include_router(users_router)  
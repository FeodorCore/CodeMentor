from fastapi import APIRouter
from app.api.admin.categories import router as categories_router
from app.api.admin.lessons import router as lessons_router

router = APIRouter(prefix="/admin", tags=["Admin Panel"])
router.include_router(categories_router)
router.include_router(lessons_router)


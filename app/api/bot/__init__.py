from fastapi import APIRouter
from app.api.bot.users import router as users_router
from app.api.bot.content import router as content_router

router = APIRouter(prefix="/bot", tags=["Telegram Bot API"])
router.include_router(users_router)
router.include_router(content_router)
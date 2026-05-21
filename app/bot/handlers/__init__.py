from aiogram import Router
from app.bot.handlers.start import router as start_router
from app.bot.handlers.categories import router as categories_router
from app.bot.handlers.lessons import router as lessons_router
from app.bot.handlers.consolidation import router as consolidation_router
# Главный роутер бота, подключающий все под-роутеры
all_routers = Router(name="all_routers")
all_routers.include_router(start_router)
all_routers.include_router(categories_router)
all_routers.include_router(lessons_router)
all_routers.include_router(consolidation_router)
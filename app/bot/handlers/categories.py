from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.api_client import ApiClient
from app.bot.keyboards.inline import get_categories_kb

router = Router(name="categories")


@router.callback_query(F.data == "menu:categories")
async def show_categories(callback: CallbackQuery, api: ApiClient):
    """Показать список всех категорий."""
    await callback.answer("Загружаю категории...")

    try:
        categories = await api.get_categories()
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка: {e}")
        return

    if not categories:
        await callback.message.edit_text(
            "📭 Категорий пока нет.\nАдминистратор ещё не добавил материалы."
        )
        return

    await callback.message.edit_text(
        "📚 <b>Выберите категорию:</b>",
        parse_mode="HTML",
        reply_markup=get_categories_kb(categories)
    )
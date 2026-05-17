from aiogram import Router, types
from services.api_client import api_client
from keyboards.menu import back_to_article_keyboard

router = Router()

@router.callback_query(lambda c: c.data and c.data.startswith("article_"))
async def show_article(callback: types.CallbackQuery):
    article_id = int(callback.data.split("_")[1])
    article = await api_client.get_article(article_id)
    if not article:
        await callback.message.edit_text("Статья не найдена.")
        return
    text = f"<b>{article['title']}</b>\n\n{article['content']}"
    # клавиатура с кнопкой "Пройти тест"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❓ Пройти тест", callback_data=f"quiz_{article_id}")],
        [InlineKeyboardButton(text="◀️ Назад к списку", callback_data="articles")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="HTML")
    await callback.answer()

# временный импорт для клавиатуры
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
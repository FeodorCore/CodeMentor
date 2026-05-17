from aiogram import Router, types
from aiogram.filters import Command
from services.api_client import api_client
from keyboards.menu import get_main_keyboard, articles_keyboard

router = Router()

@router.message(Command("menu"))
@router.callback_query(lambda c: c.data == "main_menu")
async def show_main_menu(event: types.Message | types.CallbackQuery):
    if isinstance(event, types.CallbackQuery):
        await event.message.edit_text("Главное меню:", reply_markup=get_main_keyboard())
        await event.answer()
    else:
        await event.answer("Главное меню:", reply_markup=get_main_keyboard())

@router.callback_query(lambda c: c.data == "articles")
async def show_articles(callback: types.CallbackQuery):
    articles = await api_client.get_articles()
    if not articles:
        await callback.message.edit_text("Статей пока нет.")
        return
    await callback.message.edit_text("Выберите статью:", reply_markup=articles_keyboard(articles))
    await callback.answer()
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.bot.api_client import ApiClient
from app.bot.keyboards.inline import get_main_menu_kb

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, api: ApiClient, state: FSMContext):
    """Обработчик /start — регистрация и приветствие."""
    await state.clear()

    tg_id = message.from_user.id
    username = message.from_user.username

    try:
        user = await api.sync_user(telegram_id=tg_id, username=username)
    except Exception as e:
        await message.answer(f"❌ Ошибка подключения к серверу: {e}")
        return

    greeting = (
        f"👋 Привет, <b>@{username or 'друг'}</b>!\n\n"
        f"Я бот для обучения. Выбирай категорию и читай материалы.\n\n"
        f"Твой ID в системе: <code>{user.id}</code>"
    )
    await message.answer(
        greeting,
        parse_mode="HTML",
        reply_markup=get_main_menu_kb()
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    """Команда /menu — показать главное меню."""
    await state.clear()
    await message.answer(
        "📋 <b>Главное меню</b>",
        parse_mode="HTML",
        reply_markup=get_main_menu_kb()
    )


@router.callback_query(lambda c: c.data == "menu:main")
async def callback_main_menu(callback: CallbackQuery):
    """Возврат в главное меню."""
    await callback.message.edit_text(
        "📋 <b>Главное меню</b>",
        parse_mode="HTML",
        reply_markup=get_main_menu_kb()
    )
    await callback.answer()
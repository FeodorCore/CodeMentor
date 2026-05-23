from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from app.bot.api_client import ApiClient
from app.bot.keyboards.inline import get_main_menu_kb

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message, api: ApiClient, state: FSMContext):
    await state.clear()
    tg_id = message.from_user.id if message.from_user else 0
    username = message.from_user.username if message.from_user else None
    try:
        await api.sync_user(telegram_id=tg_id, username=username)
    except Exception as e:
        await message.answer(f"❌ Ошибка подключения к серверу: {e}")
        return

    await message.answer(
        f"👋 Привет, <b>@{username or 'друг'}</b>!\n"
        f"Я твой персональный наставник по программированию.\n"
        f"Выбери категорию для обучения или пообщайся с ИИ-экспертом.",
        parse_mode="HTML",
        reply_markup=get_main_menu_kb(),
    )


@router.message(Command("menu"))
async def cmd_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "📋 <b>Главное меню</b>", parse_mode="HTML", reply_markup=get_main_menu_kb()
    )


@router.callback_query(F.data == "menu:main")
async def cb_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "📋 <b>Главное меню</b>", parse_mode="HTML", reply_markup=get_main_menu_kb()
        )
    await callback.answer()

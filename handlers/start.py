from aiogram import Router, types
from aiogram.filters import CommandStart
from services.api_client import api_client
from keyboards.menu import get_main_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    tg_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    await api_client.register_user(tg_id, username, full_name)
    await message.answer(
        f"Добро пожаловать, {full_name}!\nВыберите действие:",
        reply_markup=get_main_keyboard()
    )
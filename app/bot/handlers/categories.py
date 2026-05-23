from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.api_client import ApiClient
from app.bot.keyboards.inline import get_categories_kb, get_ai_chat_kb
from app.bot.states import AIChatFSM
from app.bot.services.llm_service import LLMService
from app.bot.llm.base import BaseLLMClient

router = Router(name="categories")


@router.callback_query(F.data == "menu:categories")
async def show_categories(callback: CallbackQuery, api: ApiClient, state: FSMContext):
    await state.clear()
    await callback.answer("Загружаю категории...")
    try:
        categories = await api.get_categories()
    except Exception as e:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(f"❌ Ошибка: {e}")
        return

    if not categories:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                "📭 Категорий пока нет. Администратор ещё не добавил материалы."
            )
        return

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "📚 <b>Выберите категорию:</b>",
            parse_mode="HTML",
            reply_markup=get_categories_kb(categories),
        )


@router.callback_query(F.data == "ai:category_helper")
async def start_category_helper(
    callback: CallbackQuery, api: ApiClient, state: FSMContext, llm: BaseLLMClient
):
    await callback.answer("Инициализация помощника...")
    try:
        categories = await api.get_categories()
    except Exception:
        categories = []

    system_prompt = LLMService.get_prompt("category_helper", {"categories": categories})
    history = [{"role": "system", "content": system_prompt}]
    await state.set_state(AIChatFSM.category_helper)
    await state.update_data(history=history, mode="category_helper")

    reply, history = await LLMService.ask(llm, history)
    await state.update_data(history=history)

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"🤖 <b>Помощник по выбору:</b>\n{reply}",
            parse_mode="HTML",
            reply_markup=get_ai_chat_kb("category_helper"),
        )
    await callback.answer()

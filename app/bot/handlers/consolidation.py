import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.bot.api_client import ApiClient
from app.bot.llm.base import BaseLLMClient
from app.bot.services.consolidation import ConsolidationService
from app.bot.keyboards.inline import get_consolidation_kb, get_lesson_nav_kb
from app.bot.states import ConsolidationFSM

logger = logging.getLogger(__name__)
router = Router(name="consolidation")


@router.callback_query(F.data.startswith("consolidate:"))
async def start_consolidation(
    callback: CallbackQuery,
    state: FSMContext,
    api: ApiClient,
    llm: BaseLLMClient,
    consolidation: ConsolidationService,
):
    data = callback.data or ""
    _, lesson_id_str, category_id_str = data.split(":")
    lesson_id, category_id = int(lesson_id_str), int(category_id_str)

    lesson = await api.get_lesson(lesson_id)
    if not lesson:
        return await callback.answer("Урок не найден", show_alert=True)

    # 1. Генерация промпта через сервис
    system_prompt = consolidation.build_system_prompt(lesson.title, lesson.content)
    history = [{"role": "system", "content": system_prompt}]

    await state.set_state(ConsolidationFSM.chatting)
    await state.update_data(
        history=history, lesson_id=lesson_id, category_id=category_id
    )

    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "🧠 <i>Инициализация нейросети...</i>", parse_mode="HTML"
        )

    # 2. Запрос к LLM через сервис
    safe_reply, history = await consolidation.ask_llm(llm, history)
    await state.update_data(history=history)

    # 3. Отправка в Telegram
    chunks = consolidation.split_text(safe_reply)
    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            await callback.message.edit_text(
                f"🧠 <b>Закрепление: {lesson.title}</b>\n\n{chunk}",
                parse_mode="HTML",
                reply_markup=get_consolidation_kb(lesson_id, category_id),
            )
        else:
            await callback.message.answer(chunk, parse_mode="HTML")
    await callback.answer()


@router.message(ConsolidationFSM.chatting, F.text)
async def process_message(
    message: Message,
    state: FSMContext,
    llm: BaseLLMClient,
    consolidation: ConsolidationService,
):
    data = await state.get_data()
    history = data.get("history", [])
    lesson_id = data.get("lesson_id", 1)
    category_id = data.get("category_id", 1)

    history.append({"role": "user", "content": message.text})

    await message.bot.send_chat_action(message.chat.id, "typing")

    safe_reply, history = await consolidation.ask_llm(llm, history)
    await state.update_data(history=history)

    chunks = consolidation.split_text(safe_reply)
    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            await message.answer(
                chunk,
                parse_mode="HTML",
                reply_markup=get_consolidation_kb(lesson_id, category_id),
            )
        else:
            await message.answer(chunk, parse_mode="HTML")


@router.callback_query(F.data.startswith("finish_consolidate:"))
async def finish_consolidation(
    callback: CallbackQuery, state: FSMContext, api: ApiClient
):
    _, lesson_id_str, category_id_str = callback.data.split(":")
    lesson_id, category_id = int(lesson_id_str), int(category_id_str)

    try:
        await api.update_progress(callback.from_user.id, lesson_id)
    except Exception as e:
        return await callback.answer(f"Ошибка сохранения: {e}", show_alert=True)

    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "🎉 <b>Отлично!</b> Тема закреплена.\n",
            parse_mode="HTML",
            reply_markup=get_lesson_nav_kb(lesson_id, category_id),
        )
    await callback.answer("Прогресс сохранен!")

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.api_client import ApiClient
from app.bot.llm.base import BaseLLMClient
from app.bot.services.llm_service import LLMService
from app.bot.states import AIChatFSM
from app.bot.keyboards.inline import get_ai_chat_kb, get_main_menu_kb

router = Router(name="ai_chat")


@router.callback_query(F.data == "ai:general")
async def start_general_chat(
    callback: CallbackQuery, state: FSMContext, llm: BaseLLMClient
):
    await state.clear()
    await state.set_state(AIChatFSM.general_chat)
    system_prompt = LLMService.get_prompt("general", {})
    history = [{"role": "system", "content": system_prompt}]
    await state.update_data(history=history, mode="general")
    reply, history = await LLMService.ask(llm, history)
    await state.update_data(history=history)
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"🤖 <b>ИИ-Эксперт:</b>\n{reply}",
            parse_mode="HTML",
            reply_markup=get_ai_chat_kb("general"),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("ai:lesson_qa:"))
async def start_lesson_qa(
    callback: CallbackQuery, api: ApiClient, state: FSMContext, llm: BaseLLMClient
):
    _, _, lesson_id_str, category_id_str = callback.data.split(":")
    lesson_id, category_id = int(lesson_id_str), int(category_id_str)
    try:
        lesson = await api.get_lesson(lesson_id)
    except Exception:
        lesson = None

    # Сохраняем контекст теста ДО очистки стейта
    data = await state.get_data()
    quiz_ctx = data.get("last_quiz_context")

    await state.clear()
    await state.set_state(AIChatFSM.lesson_qa)

    ctx = {
        "lesson_title": lesson.title if lesson else "Урок",
        "lesson_content": lesson.content if lesson else "",
        "quiz_context": quiz_ctx,  # <-- передаём контекст ответа
    }
    system_prompt = LLMService.get_prompt("lesson_qa", ctx)
    history = [{"role": "system", "content": system_prompt}]
    await state.update_data(
        history=history, mode="lesson_qa", lesson_id=lesson_id, category_id=category_id
    )
    reply, history = await LLMService.ask(llm, history)
    await state.update_data(history=history)
    if isinstance(callback.message, Message):
        await callback.message.answer(
            f"🤖 <b>Разбор ответа:</b>\n{reply}",
            parse_mode="HTML",
            reply_markup=get_ai_chat_kb("lesson_qa"),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("ai:interview:"))
async def start_interview(
    callback: CallbackQuery, api: ApiClient, state: FSMContext, llm: BaseLLMClient
):
    _, _, lesson_id_str, category_id_str = callback.data.split(":")
    lesson_id, category_id = int(lesson_id_str), int(category_id_str)
    try:
        lesson = await api.get_lesson(lesson_id)
    except Exception:
        lesson = None
    await state.clear()
    await state.set_state(AIChatFSM.interview)
    ctx = {"lesson_title": lesson.title if lesson else "Тема"}
    system_prompt = LLMService.get_prompt("interview", ctx)
    history = [{"role": "system", "content": system_prompt}]
    await state.update_data(
        history=history, mode="interview", lesson_id=lesson_id, category_id=category_id
    )
    reply, history = await LLMService.ask(llm, history)
    await state.update_data(history=history)
    if isinstance(callback.message, Message):
        await callback.message.answer(
            f"🎤 <b>Собеседование:</b>\n{reply}",
            parse_mode="HTML",
            reply_markup=get_ai_chat_kb("interview"),
        )
    await callback.answer()


@router.callback_query(F.data == "ai:stop")
async def stop_ai_chat(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.answer(
            "🛑 Диалог завершён.", reply_markup=get_main_menu_kb()
        )
    await callback.answer()


@router.message(AIChatFSM.general_chat, F.text)
@router.message(AIChatFSM.category_helper, F.text)
@router.message(AIChatFSM.lesson_qa, F.text)
@router.message(AIChatFSM.interview, F.text)
async def process_ai_message(message: Message, state: FSMContext, llm: BaseLLMClient):
    data = await state.get_data()
    history = data.get("history", [])
    mode = data.get("mode", "general")
    history.append({"role": "user", "content": message.text})
    await message.bot.send_chat_action(message.chat.id, "typing")
    reply, history = await LLMService.ask(llm, history)
    await state.update_data(history=history)
    chunks = LLMService.split_text(reply)
    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            await message.answer(
                chunk, parse_mode="HTML", reply_markup=get_ai_chat_kb(mode)
            )
        else:
            await message.answer(chunk, parse_mode="HTML")

import html
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.api_client import ApiClient
from app.bot.llm_service import OllamaClient
from app.bot.keyboards.inline import get_consolidation_kb, get_lesson_nav_kb
from app.bot.states import ConsolidationFSM

logger = logging.getLogger(__name__)
router = Router(name="consolidation")

TG_MAX_LENGTH = 4000


def _split_text(text: str, max_len: int = TG_MAX_LENGTH) -> list[str]:
    """Безопасно разбивает текст на части для Telegram."""
    if len(text) <= max_len:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:max_len])
        text = text[max_len:]
    return chunks


@router.callback_query(F.data.startswith("consolidate:"))
async def start_consolidation(
    callback: CallbackQuery, state: FSMContext, api: ApiClient, ollama: OllamaClient
):
    data = callback.data or ""
    _, lesson_id_str, category_id_str = data.split(":")
    lesson_id = int(lesson_id_str)
    category_id = int(category_id_str)

    lesson = await api.get_lesson(lesson_id)
    if not lesson:
        await callback.answer("Урок не найден", show_alert=True)
        return
    system_prompt = f"""Ты — дружелюбный преподаватель-репетитор. Ты помогаешь ученику закрепить тему урока.

    ТЕКУЩИЙ УРОК: «{lesson.title}»
    СОДЕРЖАНИЕ УРОКА:
    {lesson.content}

    ПРАВИЛА ПОВЕДЕНИЯ (СТРОГО СОБЛЮДАЙ):
    1. Отвечай ТОЛЬКО на русском языке.
    2. Начни с одного конкретного вопроса по теме урока, чтобы проверить понимание.
    3. НЕ давай готовый ответ в своём вопросе. Ученик должен ответить сам.
    4. Жди ответа ученика. После его ответа:
    - Если ответ верный: коротко похвали и задай следующий уточняющий вопрос.
    - Если ответ неверный или неполный: мягко укажи на ошибку, дай подсказку (но не полный ответ) и попроси попробовать ещё раз.
    5. Отвечай коротко — 1-3 предложения за реплику. Не пиши лекций.
    6. НЕ повторяй один и тот же вопрос дважды.
    7. Не используй markdown-разметку, пиши простым текстом.
    8. Если ученик отвечает "не знаю" или просит помощи — дай объяснение и задай более простой вопрос.

    Начни диалог с приветствия и первого вопроса по теме урока."""

    history = [{"role": "system", "content": system_prompt}]
    await state.set_state(ConsolidationFSM.chatting)
    await state.update_data(
        history=history,
        lesson_id=lesson_id,
        category_id=category_id,
        lesson_title=lesson.title,
    )
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "🧠 <i>Инициализация нейросети...</i>", parse_mode="HTML"
        )

    llm_reply = await ollama.chat(history)
    history.append({"role": "assistant", "content": llm_reply})
    await state.update_data(history=history)

    # Экранируем HTML-символы из ответа LLM, чтобы не сломать parse_mode
    safe_reply = html.escape(llm_reply)
    chunks = _split_text(safe_reply)

    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            if isinstance(callback.message, Message):
                await callback.message.edit_text(
                    f"🧠 <b>Закрепление темы: {html.escape(lesson.title)}</b>\n\n{chunk}",
                    parse_mode="HTML",
                    reply_markup=get_consolidation_kb(lesson_id, category_id),
                )
        else:
            if isinstance(callback.message, Message):
                await callback.message.answer(chunk, parse_mode="HTML")

    await callback.answer()


@router.message(ConsolidationFSM.chatting, F.text)
async def process_consolidation_message(
    message: Message, state: FSMContext, ollama: OllamaClient
):
    data = await state.get_data()
    history = data.get("history", [])
    lesson_id = data.get("lesson_id") or 1
    category_id = data.get("category_id") or 1

    history.append({"role": "user", "content": message.text})
    history = ollama.trim_history(history, max_messages=12)
    await state.update_data(history=history)
    if isinstance(message.bot, Message):
        await message.bot.send_chat_action(message.chat.id, "typing")

    llm_reply = await ollama.chat(history)
    history.append({"role": "assistant", "content": llm_reply})
    await state.update_data(history=history)

    safe_reply = html.escape(llm_reply)
    chunks = _split_text(safe_reply)
    for i, chunk in enumerate(chunks):
        if i == len(chunks) - 1:
            await message.answer(
                chunk, reply_markup=get_consolidation_kb(lesson_id, category_id)
            )
        else:
            await message.answer(chunk)


@router.callback_query(F.data.startswith("finish_consolidate:"))
async def finish_consolidation(
    callback: CallbackQuery, state: FSMContext, api: ApiClient
):
    data = callback.data or ""
    _, lesson_id_str, category_id_str = data.split(":")
    lesson_id = int(lesson_id_str)
    category_id = int(category_id_str)
    tg_id = callback.from_user.id

    try:
        await api.update_progress(tg_id, lesson_id)
    except Exception as e:
        logger.error(f"Ошибка сохранения прогресса: {e}")
        await callback.answer(f"Ошибка сохранения прогресса: {e}", show_alert=True)
        return

    await state.clear()
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "🎉 <b>Отлично!</b> Тема закреплена, прогресс сохранен.\n"
            "Ты можешь вернуться к списку уроков или выбрать новую категорию.",
            parse_mode="HTML",
            reply_markup=get_lesson_nav_kb(lesson_id, category_id),
        )
    await callback.answer("Прогресс сохранен!")

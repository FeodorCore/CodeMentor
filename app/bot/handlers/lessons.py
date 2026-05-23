from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from app.bot.api_client import ApiClient
from app.bot.keyboards.inline import (
    get_lessons_kb,
    get_lesson_actions_kb,
    get_quiz_option_kb,
    get_after_quiz_kb,
)
from app.bot.states import QuizFSM
from app.bot.handlers.categories import router as _  # keep import structure clean

router = Router(name="lessons")


@router.callback_query(F.data.startswith("category:"))
async def show_lessons(callback: CallbackQuery, api: ApiClient, state: FSMContext):
    await state.clear()
    category_id = int(callback.data.split(":")[1])
    tg_id = callback.from_user.id
    await callback.answer("Загружаю уроки...")
    try:
        lessons = await api.get_lessons(category_id)
        completed_ids = await api.get_completed_lessons(tg_id, category_id)
    except Exception as e:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(f"❌ Ошибка: {e}")
        return
    if not lessons:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                "📭 В этой категории пока нет уроков.",
                reply_markup=get_back_to_cats_kb(),
            )
        return
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            "📄 <b>Выберите урок:</b>\n",
            parse_mode="HTML",
            reply_markup=get_lessons_kb(lessons, category_id, completed_ids),
        )


def get_back_to_cats_kb():
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="◀️ К категориям", callback_data="menu:categories"
                )
            ]
        ]
    )


@router.callback_query(F.data.startswith("lesson:"))
async def show_lesson(callback: CallbackQuery, api: ApiClient, state: FSMContext):
    await state.clear()
    lesson_id = int(callback.data.split(":")[1])
    await callback.answer("Загружаю материал...")
    try:
        lesson = await api.get_lesson(lesson_id)
    except Exception as e:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(f"❌ Ошибка: {e}")
        return
    if not lesson:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                "❌ Урок не найден.", reply_markup=get_back_to_cats_kb()
            )
        return
    text = f"📖 <b>{lesson.title}</b>\n{lesson.content}"
    kb = get_lesson_actions_kb(lesson.id, lesson.category_id)
    if isinstance(callback.message, Message):
        if len(text) > 4000:
            await callback.message.edit_text(text[:4000], parse_mode="HTML")
            await callback.message.answer(
                text[4000:], parse_mode="HTML", reply_markup=kb
            )
        else:
            await callback.message.edit_text(text, parse_mode="HTML", reply_markup=kb)


@router.callback_query(F.data.startswith("quiz:start:"))
async def start_quiz(callback: CallbackQuery, api: ApiClient, state: FSMContext):
    _, _, lesson_id_str, category_id_str = callback.data.split(":")
    lesson_id, category_id = int(lesson_id_str), int(category_id_str)
    tg_id = callback.from_user.id
    await callback.answer("Подготовка теста...")
    try:
        questions = await api.get_questions(lesson_id)
        await api.update_progress(tg_id, lesson_id)
    except Exception as e:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(f"❌ Ошибка загрузки теста: {e}")
        return
    if not questions:
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                "✅ Материал отмечен как изученный. Тестов для этого урока нет.",
                reply_markup=get_after_quiz_kb(True, lesson_id, category_id),
            )
        return
    await state.set_state(QuizFSM.active)
    await state.update_data(
        questions=questions, current_idx=0, lesson_id=lesson_id, category_id=category_id
    )
    q = questions[0]
    if isinstance(callback.message, Message):
        await callback.message.edit_text(
            f"📝 <b>Вопрос 1/{len(questions)}:</b>\n{q['text']}",
            parse_mode="HTML",
            reply_markup=get_quiz_option_kb(
                q["id"], q["answers"], lesson_id, category_id
            ),
        )


@router.callback_query(QuizFSM.active, F.data.startswith("quiz:answer:"))
async def handle_quiz_answer(
    callback: CallbackQuery, api: ApiClient, state: FSMContext
):
    _, _, ans_id_str, is_correct_str, lesson_id_str, category_id_str = (
        callback.data.split(":")
    )
    ans_id = int(ans_id_str)
    is_correct = is_correct_str.lower() == "true"
    lesson_id = int(lesson_id_str)
    category_id = int(category_id_str)
    tg_id = callback.from_user.id
    await callback.answer()
    try:
        await api.submit_answer(tg_id, ans_id, is_correct)
    except Exception:
        pass

    data = await state.get_data()
    questions = data.get("questions", [])
    idx = data.get("current_idx", 0)

    # === СОХРАНЯЕМ КОНТЕКСТ ВОПРОСА ДЛЯ ИИ ===
    q = questions[idx] if idx < len(questions) else None
    user_ans_text = "Не указан"
    correct_ans_text = "Не указан"
    if q:
        for a in q.get("answers", []):
            if a["id"] == ans_id:
                user_ans_text = a["text"]
            if a.get("is_correct"):
                correct_ans_text = a["text"]

    await state.update_data(
        last_quiz_context={
            "question": q["text"] if q else "",
            "user_answer": user_ans_text,
            "correct_answer": correct_ans_text,
            "is_correct": is_correct,
        }
    )
    # ========================================

    msg = (
        "✅ Верно! Отличная работа."
        if is_correct
        else "❌ Неверно. Ответ сохранён. Вы можете спросить у ИИ пояснение."
    )

    if idx + 1 < len(questions):
        next_idx = idx + 1
        await state.update_data(current_idx=next_idx)
        q = questions[next_idx]
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                f"{msg}\n📝 <b>Вопрос {next_idx + 1}/{len(questions)}:</b>\n{q['text']}",
                parse_mode="HTML",
                reply_markup=get_quiz_option_kb(
                    q["id"], q["answers"], lesson_id, category_id
                ),
            )
    else:
        await state.clear()
        if isinstance(callback.message, Message):
            await callback.message.edit_text(
                f"{msg}\n🎉 Тест завершён! Прогресс сохранён.",
                parse_mode="HTML",
                reply_markup=get_after_quiz_kb(is_correct, lesson_id, category_id),
            )

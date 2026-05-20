from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.bot.api_client import ApiClient
from app.bot.keyboards.inline import get_lessons_kb, get_lesson_nav_kb, get_back_to_categories_kb

router = Router(name="lessons")


@router.callback_query(F.data.startswith("category:"))
async def show_lessons(callback: CallbackQuery, api: ApiClient):
    """Показать список уроков в выбранной категории с отметками пройденных."""
    category_id = int(callback.data.split(":")[1])
    tg_id = callback.from_user.id
    await callback.answer("Загружаю уроки...")

    try:
        lessons = await api.get_lessons(category_id)
        completed_ids = await api.get_completed_lessons(tg_id, category_id)
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка: {e}")
        return

    if not lessons:
        await callback.message.edit_text(
            "📭 В этой категории пока нет уроков.",
            reply_markup=get_back_to_categories_kb()
        )
        return

    await callback.message.edit_text(
        "📄 <b>Выберите урок:</b>\n\n"
        "✅ — пройденные уроки",
        parse_mode="HTML",
        reply_markup=get_lessons_kb(lessons, category_id, completed_ids)
    )


@router.callback_query(F.data.startswith("lesson:"))
async def show_lesson_content(callback: CallbackQuery, api: ApiClient):
    """Показать содержимое урока."""
    lesson_id = int(callback.data.split(":")[1])
    await callback.answer("Загружаю урок...")

    try:
        lesson = await api.get_lesson(lesson_id)
    except Exception as e:
        await callback.message.edit_text(f"❌ Ошибка: {e}")
        return

    if not lesson:
        await callback.message.edit_text(
            "❌ Урок не найден.",
            reply_markup=get_back_to_categories_kb()
        )
        return

    text = (
        f"📖 <b>{lesson.title}</b>\n\n"
        f"{lesson.content}"
    )

    # Telegram ограничивает сообщение 4096 символами
    if len(text) > 4000:
        first_part = text[:4000]
        await callback.message.edit_text(first_part, parse_mode="HTML")
        await callback.message.answer(
            text[4000:],
            parse_mode="HTML",
            reply_markup=get_lesson_nav_kb(lesson.id, lesson.category_id)
        )
    else:
        await callback.message.edit_text(
            text,
            parse_mode="HTML",
            reply_markup=get_lesson_nav_kb(lesson.id, lesson.category_id)
        )
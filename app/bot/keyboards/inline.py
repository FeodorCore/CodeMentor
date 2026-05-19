from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.api_client import CategoryDTO, LessonDTO


def get_main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Категории", callback_data="menu:categories")],
    ])


def get_categories_kb(categories: list[CategoryDTO]) -> InlineKeyboardMarkup:
    """Клавиатура со списком категорий."""
    buttons = []
    for cat in categories:
        buttons.append([
            InlineKeyboardButton(
                text=f"📂 {cat.name}",
                callback_data=f"category:{cat.id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lessons_kb(
    lessons: list[LessonDTO],
    category_id: int,
    completed_ids: list[int]
) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком уроков в категории.
    Пройденные уроки отмечаются галочкой ✅.
    """
    buttons = []
    for lesson in lessons:
        is_done = lesson.id in completed_ids
        prefix = "✅ " if is_done else "📄 "
        buttons.append([
            InlineKeyboardButton(
                text=f"{prefix}{lesson.sort_order}. {lesson.title}",
                callback_data=f"lesson:{lesson.id}"
            )
        ])
    buttons.append([
        InlineKeyboardButton(text="◀️ К категориям", callback_data="menu:categories")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lesson_nav_kb(lesson_id: int, category_id: int) -> InlineKeyboardMarkup:
    """Навигация после просмотра урока (только возврат к списку)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ К списку уроков", callback_data=f"category:{category_id}")],
    ])


def get_back_to_categories_kb() -> InlineKeyboardMarkup:
    """Кнопка возврата к категориям."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ К категориям", callback_data="menu:categories")],
    ])
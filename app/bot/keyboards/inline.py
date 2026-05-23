from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.bot.api_client import CategoryDTO, LessonDTO


def get_main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📚 Выбрать категорию", callback_data="menu:categories"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Разобрать с ИИ", callback_data="ai:general"
                )
            ],
        ]
    )


def get_categories_kb(categories: list[CategoryDTO]) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"📂 {c.name}", callback_data=f"category:{c.id}")]
        for c in categories
    ]
    buttons.append(
        [
            InlineKeyboardButton(
                text="🤖 ИИ поможет подобрать категорию",
                callback_data="ai:category_helper",
            )
        ]
    )
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lessons_kb(
    lessons: list[LessonDTO], category_id: int, completed_ids: list[int]
) -> InlineKeyboardMarkup:
    buttons = []
    for l in lessons:
        prefix = "✅ " if l.id in completed_ids else "📄 "
        buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{prefix}{l.sort_order}. {l.title}",
                    callback_data=f"lesson:{l.id}",
                )
            ]
        )
    buttons.append(
        [InlineKeyboardButton(text="◀️ К категориям", callback_data="menu:categories")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_lesson_actions_kb(lesson_id: int, category_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Ознакомился с материалом",
                    callback_data=f"quiz:start:{lesson_id}:{category_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❓ Задать вопрос у ИИ",
                    callback_data=f"ai:lesson_qa:{lesson_id}:{category_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🎤 Пройти собеседование",
                    callback_data=f"ai:interview:{lesson_id}:{category_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="◀️ К урокам", callback_data=f"category:{category_id}"
                )
            ],
        ]
    )


def get_quiz_option_kb(
    question_id: int, answers: list[dict], lesson_id: int, category_id: int
) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text=a["text"],
                callback_data=f"quiz:answer:{a['id']}:{a['is_correct']}:{lesson_id}:{category_id}",
            )
        ]
        for a in answers
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_after_quiz_kb(
    is_correct: bool, lesson_id: int, category_id: int
) -> InlineKeyboardMarkup:
    buttons = []
    if not is_correct:
        buttons.append(
            [
                InlineKeyboardButton(
                    text="🤖 Спросить у ИИ",
                    callback_data=f"ai:lesson_qa:{lesson_id}:{category_id}",
                )
            ]
        )
    buttons.append(
        [
            InlineKeyboardButton(
                text="◀️ К урокам", callback_data=f"category:{category_id}"
            )
        ]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_ai_chat_kb(mode: str) -> InlineKeyboardMarkup:
    if mode == "category_helper":
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Выбрать категорию вручную",
                        callback_data="menu:categories",
                    )
                ],
            ]
        )
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛑 Завершить диалог", callback_data="ai:stop")],
        ]
    )


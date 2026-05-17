from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Статьи", callback_data="articles")]
    ])
    return keyboard

def articles_keyboard(articles):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for article in articles:
        kb.inline_keyboard.append([InlineKeyboardButton(text=article["title"], callback_data=f"article_{article['id']}")])
    kb.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")])
    return kb

def quiz_answer_keyboard(question_id: int, answers: list):
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    for ans in answers:
        kb.inline_keyboard.append([InlineKeyboardButton(text=ans["text"], callback_data=f"answer_{question_id}_{ans['id']}")])
    return kb

def back_to_article_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад к статье", callback_data="back_to_article")]
    ])
    return kb
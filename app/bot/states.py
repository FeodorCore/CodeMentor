from aiogram.fsm.state import StatesGroup, State


class AIChatFSM(StatesGroup):
    general_chat = State()
    category_helper = State()
    lesson_qa = State()
    interview = State()


class QuizFSM(StatesGroup):
    active = State()


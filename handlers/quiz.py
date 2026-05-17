from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from services.api_client import api_client
from keyboards.menu import quiz_answer_keyboard, back_to_article_keyboard
from states.quiz import QuizState

router = Router()

@router.callback_query(lambda c: c.data and c.data.startswith("quiz_"))
async def start_quiz(callback: types.CallbackQuery, state: FSMContext):
    article_id = int(callback.data.split("_")[1])
    quiz_data = await api_client.get_quiz(article_id)
    if not quiz_data or not quiz_data["questions"]:
        await callback.message.edit_text("Вопросов для этой статьи нет.")
        return
    # сохраняем в состояние
    await state.update_data(questions=quiz_data["questions"], current_index=0, correct_count=0)
    await ask_question(callback.message, state, quiz_data["questions"][0])
    await callback.answer()

async def ask_question(message: types.Message, state: FSMContext, question: dict):
    text = question["text"]
    kb = quiz_answer_keyboard(question["id"], question["answers"])
    await message.edit_text(text, reply_markup=kb)
    await state.set_state(QuizState.waiting_for_answer)

@router.callback_query(QuizState.waiting_for_answer, F.data.startswith("answer_"))
async def process_answer(callback: types.CallbackQuery, state: FSMContext):
    _, question_id, answer_id = callback.data.split("_")
    question_id = int(question_id)
    answer_id = int(answer_id)
    tg_id = callback.from_user.id
    result = await api_client.check_answer(tg_id, question_id, answer_id)
    data = await state.get_data()
    questions = data["questions"]
    current_index = data["current_index"]
    correct_count = data["correct_count"]
    if result["correct"]:
        correct_count += 1
    # если есть следующий вопрос
    if current_index + 1 < len(questions):
        current_index += 1
        await state.update_data(current_index=current_index, correct_count=correct_count)
        await callback.message.edit_text(result["explanation"])
        # ждём 1 секунду и показываем следующий вопрос
        import asyncio
        await asyncio.sleep(1)
        await ask_question(callback.message, state, questions[current_index])
        await callback.answer()
    else:
        # тест окончен
        total = len(questions)
        final_text = f"Тест завершён!\nПравильных ответов: {correct_count} из {total}"
        await callback.message.edit_text(final_text, reply_markup=back_to_article_keyboard())
        await state.clear()
        await callback.answer()

@router.callback_query(lambda c: c.data == "back_to_article")
async def back_to_article(callback: types.CallbackQuery):
    # просто вернёмся в главное меню (или можно восстановить последнюю статью - упростим)
    await callback.message.edit_text("Главное меню:", reply_markup=get_main_keyboard())
    await callback.answer()

from keyboards.menu import get_main_keyboard
from crud import *
from init_db import init_database

# инициализируем БД (если ещё нет)
init_database()

# 1. Создаём категорию
cat_id = create_category("Python")
print("Category id:", cat_id)

# 2. Создаём статью
art_id = create_article(cat_id, "Основы Python", "Содержание статьи...", status="published")
print("Article id:", art_id)

# 3. Создаём вопрос
q_id = create_question(art_id, "Что такое PEP 8?")
print("Question id:", q_id)

# 4. Создаём ответы
a1 = create_answer(q_id, "Стандарт кодирования", is_correct=True)
a2 = create_answer(q_id, "Менеджер пакетов", is_correct=False)
print("Answers ids:", a1, a2)

# 5. Регистрируем пользователя
user_id = register_user(123456, "testuser", "Test User")
print("User id:", user_id)

# 6. Сохраняем ответ пользователя
save_user_answer(user_id, q_id, a1, is_right=True)

# 7. Проверяем историю
history = get_user_history_for_article(user_id, art_id)
print("History:", history)

print("Все тесты прошли успешно")
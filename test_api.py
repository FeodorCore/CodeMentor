import requests
import json

BASE_URL = "http://localhost:8000"
API_KEY = "supersecret-api-key-2025"
HEADERS = {"X-API-Key": API_KEY, "Content-Type": "application/json"}

def test_health():
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "API is running"}
    print("✓ Health check passed")

def test_list_articles():
    response = requests.get(f"{BASE_URL}/articles", headers=HEADERS)
    assert response.status_code == 200
    articles = response.json()
    assert isinstance(articles, list)
    print(f"✓ Got {len(articles)} articles")

def test_get_article_by_id():
    # используем article_id=1 (создан в test_crud.py)
    article_id = 1
    response = requests.get(f"{BASE_URL}/articles/{article_id}", headers=HEADERS)
    if response.status_code == 404:
        print("⚠ Article 1 not found, skipping test. Run test_crud.py first.")
        return
    assert response.status_code == 200
    article = response.json()
    assert article["id"] == article_id
    assert "content" in article
    print(f"✓ Got article: {article['title']}")

def test_get_quiz():
    article_id = 1
    response = requests.get(f"{BASE_URL}/articles/{article_id}/quiz", headers=HEADERS)
    if response.status_code == 404:
        print("⚠ Article 1 not found, skipping quiz test.")
        return
    assert response.status_code == 200
    quiz = response.json()
    assert quiz["article_id"] == article_id
    assert "questions" in quiz
    assert len(quiz["questions"]) > 0
    # проверяем, что у вопроса есть ответы без is_correct
    q = quiz["questions"][0]
    assert "answers" in q
    assert "is_correct" not in q["answers"][0]
    print("✓ Quiz data correct (no is_correct exposed)")

def test_register_user():
    payload = {
        "tg_id": 999888,
        "username": "testuser2",
        "full_name": "Test User Two"
    }
    response = requests.post(f"{BASE_URL}/users/register", headers=HEADERS, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    print(f"✓ Registered user with id {data['user_id']}")

def test_check_answer():
    # требуется существующий пользователь (tg_id=123456 из test_crud.py) и вопрос с ответами
    # предполагаем, что вопрос id=1, ответ id=1 (правильный)
    payload = {
        "tg_id": 123456,
        "question_id": 1,
        "answer_id": 1
    }
    response = requests.post(f"{BASE_URL}/quiz/check", headers=HEADERS, json=payload)
    if response.status_code == 404:
        print("⚠ User 123456 or question 1 not found. Run test_crud.py first.")
        return
    assert response.status_code == 200
    result = response.json()
    assert "correct" in result
    print(f"✓ Answer check result: {result}")

def test_user_history():
    tg_id = 123456
    response = requests.get(f"{BASE_URL}/users/{tg_id}/history?article_id=1", headers=HEADERS)
    if response.status_code == 404:
        print("⚠ User not found, skipping history test.")
        return
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    print(f"✓ Got history for user {tg_id}: {len(history)} records")

def run_all_tests():
    print("=== Testing API endpoints ===\n")
    test_health()
    test_list_articles()
    test_get_article_by_id()
    test_get_quiz()
    test_register_user()
    test_check_answer()
    test_user_history()
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    run_all_tests()
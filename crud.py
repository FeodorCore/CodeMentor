from database import db
from typing import List, Optional

# ---------- Category ----------
def create_category(name: str, parent_id: Optional[int] = None) -> int:
    cursor = db.execute(
        "INSERT INTO Category (name, parent_id) VALUES (?, ?)",
        (name, parent_id)
    )
    return cursor.lastrowid

def get_category(category_id: int) -> Optional[dict]:
    row = db.fetch_one("SELECT * FROM Category WHERE id = ?", (category_id,))
    return dict(row) if row else None

def get_categories() -> List[dict]:
    rows = db.fetch_all("SELECT * FROM Category ORDER BY id")
    return [dict(row) for row in rows]

def update_category(category_id: int, name: str, parent_id: Optional[int] = None) -> bool:
    db.execute(
        "UPDATE Category SET name = ?, parent_id = ? WHERE id = ?",
        (name, parent_id, category_id)
    )
    return True

def delete_category(category_id: int) -> bool:
    db.execute("DELETE FROM Category WHERE id = ?", (category_id,))
    return True

# ---------- Article ----------
def create_article(category_id: int, title: str, content: str = None,
                   schedule_at: str = None, status: str = "draft") -> int:
    cursor = db.execute(
        "INSERT INTO Article (category_id, title, content, schedule_at, status) VALUES (?, ?, ?, ?, ?)",
        (category_id, title, content, schedule_at, status)
    )
    return cursor.lastrowid

def get_article(article_id: int) -> Optional[dict]:
    row = db.fetch_one("SELECT * FROM Article WHERE id = ?", (article_id,))
    return dict(row) if row else None

def get_articles_by_category(category_id: int) -> List[dict]:
    rows = db.fetch_all("SELECT * FROM Article WHERE category_id = ?", (category_id,))
    return [dict(row) for row in rows]

def get_all_articles() -> List[dict]:
    rows = db.fetch_all("SELECT * FROM Article ORDER BY created_at DESC")
    return [dict(row) for row in rows]

def update_article(article_id: int, **kwargs):
    allowed = ["category_id", "title", "content", "schedule_at", "status"]
    updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
    if not updates:
        return
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [article_id]
    db.execute(f"UPDATE Article SET {set_clause} WHERE id = ?", tuple(values))

def delete_article(article_id: int):
    db.execute("DELETE FROM Article WHERE id = ?", (article_id,))

# ---------- Question ----------
def create_question(article_id: int, text: str) -> int:
    cursor = db.execute("INSERT INTO Question (article_id, text) VALUES (?, ?)", (article_id, text))
    return cursor.lastrowid

def get_questions_by_article(article_id: int) -> List[dict]:
    rows = db.fetch_all("SELECT * FROM Question WHERE article_id = ?", (article_id,))
    return [dict(row) for row in rows]

def delete_question(question_id: int):
    db.execute("DELETE FROM Question WHERE id = ?", (question_id,))

# ---------- Answer ----------
def create_answer(question_id: int, text: str, is_correct: bool = False) -> int:
    cursor = db.execute(
        "INSERT INTO Answer (question_id, text, is_correct) VALUES (?, ?, ?)",
        (question_id, text, is_correct)
    )
    return cursor.lastrowid

def get_answers_by_question(question_id: int) -> List[dict]:
    rows = db.fetch_all("SELECT * FROM Answer WHERE question_id = ?", (question_id,))
    return [dict(row) for row in rows]

def delete_answer(answer_id: int):
    db.execute("DELETE FROM Answer WHERE id = ?", (answer_id,))

# ---------- Users ----------
def register_user(tg_id: int, username: str = None, full_name: str = None) -> int:
    # если уже есть — возвращаем id
    existing = db.fetch_one("SELECT id FROM Users WHERE tg_id = ?", (tg_id,))
    if existing:
        return existing["id"]
    cursor = db.execute(
        "INSERT INTO Users (tg_id, username, full_name) VALUES (?, ?, ?)",
        (tg_id, username, full_name)
    )
    return cursor.lastrowid

def get_user_by_tg_id(tg_id: int) -> Optional[dict]:
    row = db.fetch_one("SELECT * FROM Users WHERE tg_id = ?", (tg_id,))
    return dict(row) if row else None

def set_user_active(tg_id: int, is_active: bool):
    db.execute("UPDATE Users SET is_active = ? WHERE tg_id = ?", (is_active, tg_id))

# ---------- UserHistory ----------
def save_user_answer(user_id: int, question_id: int, answer_id: int, is_right: bool) -> int:
    cursor = db.execute(
        "INSERT INTO UserHistory (user_id, question_id, answer_id, is_right) VALUES (?, ?, ?, ?)",
        (user_id, question_id, answer_id, is_right)
    )
    return cursor.lastrowid

def get_user_history_for_article(user_id: int, article_id: int) -> List[dict]:
    rows = db.fetch_all("""
        SELECT uh.*, q.article_id
        FROM UserHistory uh
        JOIN Question q ON uh.question_id = q.id
        WHERE uh.user_id = ? AND q.article_id = ?
        ORDER BY uh.created_at
    """, (user_id, article_id))
    return [dict(row) for row in rows]

# ---------- MailingLog ----------
def log_mailing(article_id: int, user_id: int) -> int:
    cursor = db.execute(
        "INSERT INTO MailingLog (article_id, user_id) VALUES (?, ?)",
        (article_id, user_id)
    )
    return cursor.lastrowid

def was_article_sent_to_user(article_id: int, user_id: int) -> bool:
    row = db.fetch_one(
        "SELECT id FROM MailingLog WHERE article_id = ? AND user_id = ?",
        (article_id, user_id)
    )
    return row is not None
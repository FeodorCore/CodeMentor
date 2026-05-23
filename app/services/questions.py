import sqlite3
import json
from app.models.questions import (
    QuestionCreate,
    QuestionResponse,
    AnswerOptionResponse,
    AnswerOptionCreate,
)


class QuestionService:
    """Сервис для работы с вопросами и вариантами ответов."""

    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_by_lesson(self, lesson_id: int) -> list[QuestionResponse]:
        """Получить все вопросы урока с вариантами ответов."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # Получаем вопросы
            cursor.execute(
                "SELECT id, lesson_id, text, sort_order FROM Question "
                "WHERE lesson_id = ? ORDER BY sort_order ASC, id ASC",
                (lesson_id,),
            )
            questions_rows = cursor.fetchall()

            result = []
            for q_row in questions_rows:
                q_dict = dict(q_row)
                # Получаем варианты ответов для каждого вопроса
                cursor.execute(
                    "SELECT id, question_id, text, is_correct, sort_order "
                    "FROM AnswerOption WHERE question_id = ? "
                    "ORDER BY sort_order ASC, id ASC",
                    (q_dict["id"],),
                )
                answers = [AnswerOptionResponse(**dict(a)) for a in cursor.fetchall()]
                result.append(QuestionResponse(**q_dict, answers=answers))

            return result
        finally:
            conn.close()

    def replace_questions_for_lesson(
        self, lesson_id: int, questions: list[QuestionCreate]
    ) -> list[QuestionResponse]:
        """
        Полностью заменить все вопросы урока на новые (транзакционно).
        Удаляет старые вопросы (и ответы через CASCADE), создаёт новые.
        """
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            # 1. Удаляем все старые вопросы урока (CASCADE удалит ответы)
            cursor.execute("DELETE FROM Question WHERE lesson_id = ?", (lesson_id,))

            result = []
            # 2. Создаём новые вопросы и ответы
            for q in questions:
                cursor.execute(
                    "INSERT INTO Question (lesson_id, text, sort_order) VALUES (?, ?, ?)",
                    (lesson_id, q.text, q.sort_order),
                )
                question_id = cursor.lastrowid

                answers_result = []
                for a in q.answers:
                    cursor.execute(
                        "INSERT INTO AnswerOption (question_id, text, is_correct, sort_order) "
                        "VALUES (?, ?, ?, ?)",
                        (question_id, a.text, a.is_correct, a.sort_order),
                    )
                    answers_result.append(
                        AnswerOptionResponse(
                            id=cursor.lastrowid,
                            question_id=question_id,
                            text=a.text,
                            is_correct=a.is_correct,
                            sort_order=a.sort_order,
                        )
                    )

                result.append(
                    QuestionResponse(
                        id=question_id,
                        lesson_id=lesson_id,
                        text=q.text,
                        sort_order=q.sort_order,
                        answers=answers_result,
                    )
                )

            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def get_questions_count(self, lesson_id: int) -> int:
        """Получить количество вопросов для урока."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM Question WHERE lesson_id = ?",
                (lesson_id,),
            )
            row = cursor.fetchone()
            return row["cnt"] if row else 0
        finally:
            conn.close()

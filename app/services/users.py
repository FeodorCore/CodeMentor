import sqlite3
from app.models.users import (
    UserResponse,
    UserProgressResponse,
    LessonProgressDetail,
    UserAnswerDetail,
)


class UserService:
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_all(self) -> list[UserResponse]:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, telegram_id, username, is_admin FROM User ORDER BY id ASC"
            )
            return [UserResponse(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def get_by_id(self, user_id: int) -> UserResponse | None:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, telegram_id, username, is_admin FROM User WHERE id = ?",
                (user_id,),
            )
            row = cursor.fetchone()
            return UserResponse(**dict(row)) if row else None
        finally:
            conn.close()

    def get_by_telegram_id(self, telegram_id: int) -> UserResponse | None:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, telegram_id, username, is_admin FROM User WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = cursor.fetchone()
            return UserResponse(**dict(row)) if row else None
        finally:
            conn.close()

    def sync_user(self, telegram_id: int, username: str | None) -> UserResponse:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, telegram_id, username, is_admin FROM User WHERE telegram_id = ?",
                (telegram_id,),
            )
            row = cursor.fetchone()
            if row:
                if row["username"] != username:
                    cursor.execute(
                        "UPDATE User SET username = ? WHERE telegram_id = ?",
                        (username, telegram_id),
                    )
                    conn.commit()
                return UserResponse(**dict(row))
            else:
                cursor.execute(
                    "INSERT INTO User (telegram_id, username) VALUES (?, ?)",
                    (telegram_id, username),
                )
                conn.commit()
                return self.get_by_telegram_id(telegram_id)
        finally:
            conn.close()


class UserProgressService:
    def __init__(self, db_name: str = "app.db"):
        self.db_name = db_name

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def get_by_user(
        self, user_id: int, category_id: int | None = None
    ) -> list[UserProgressResponse]:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            query = """
                SELECT up.id, up.user_id, up.lesson_id, up.learned, up.completed_at,
                       l.title as lesson_title, l.category_id, c.name as category_name
                FROM UserProgress up
                JOIN Lesson l ON up.lesson_id = l.id
                JOIN Category c ON l.category_id = c.id
                WHERE up.user_id = ?
            """
            params = [user_id]
            if category_id is not None:
                query += " AND l.category_id = ?"
                params.append(category_id)
            query += " ORDER BY c.id ASC, l.sort_order ASC"
            cursor.execute(query, params)
            return [UserProgressResponse(**dict(row)) for row in cursor.fetchall()]
        finally:
            conn.close()

    def mark_completed(self, user_id: int, lesson_id: int) -> bool:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO UserProgress (user_id, lesson_id, learned)
                   VALUES (?, ?, TRUE)
                   ON CONFLICT(user_id, lesson_id)
                   DO UPDATE SET learned = TRUE, completed_at = CURRENT_TIMESTAMP""",
                (user_id, lesson_id),
            )
            conn.commit()
            return True
        finally:
            conn.close()

    def get_next_lesson_id(self, user_id: int, category_id: int) -> int | None:
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """SELECT l.id FROM Lesson l
                   LEFT JOIN UserProgress up ON l.id = up.lesson_id AND up.user_id = ?
                   WHERE l.category_id = ? AND (up.learned IS NULL OR up.learned = FALSE)
                   ORDER BY l.sort_order ASC LIMIT 1""",
                (user_id, category_id),
            )
            row = cursor.fetchone()
            return row["id"] if row else None
        finally:
            conn.close()

    def get_detailed_progress(
        self, user_id: int, category_id: int | None = None
    ) -> list[LessonProgressDetail]:
        """Возвращает прогресс пользователя с привязанными ответами на тесты."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()

            # 1. Загружаем прогресс по урокам
            prog_query = """
                SELECT up.lesson_id, up.learned, up.completed_at,
                       l.title as lesson_title, l.sort_order, l.category_id,
                       c.name as category_name
                FROM UserProgress up
                JOIN Lesson l ON up.lesson_id = l.id
                JOIN Category c ON l.category_id = c.id
                WHERE up.user_id = ?
            """
            prog_params = [user_id]
            if category_id is not None:
                prog_query += " AND l.category_id = ?"
                prog_params.append(category_id)
            prog_query += " ORDER BY c.id ASC, l.sort_order ASC"

            cursor.execute(prog_query, prog_params)
            prog_rows = cursor.fetchall()

            lessons_map: dict[int, LessonProgressDetail] = {}
            for row in prog_rows:
                d = dict(row)
                lid = d["lesson_id"]
                lessons_map[lid] = LessonProgressDetail(
                    lesson_id=lid,
                    lesson_title=d["lesson_title"],
                    sort_order=d["sort_order"],
                    category_id=d["category_id"],
                    category_name=d["category_name"],
                    learned=bool(d["learned"]),
                    completed_at=d["completed_at"],
                    answers=[],
                )

            # 2. Загружаем ответы пользователя
            ans_query = """
                SELECT ua.id, ua.is_correct, ua.answered_at,
                       q.text as question_text, q.lesson_id,
                       l.category_id,
                       ao_user.text as user_answer_text,
                       (SELECT text FROM AnswerOption WHERE question_id = q.id AND is_correct = 1 LIMIT 1) as correct_answer_text
                FROM UserAnswer ua
                JOIN AnswerOption ao_user ON ua.answer_option_id = ao_user.id
                JOIN Question q ON ao_user.question_id = q.id
                JOIN Lesson l ON q.lesson_id = l.id
                WHERE ua.user_id = ?
            """
            ans_params = [user_id]
            if category_id is not None:
                ans_query += " AND l.category_id = ?"
                ans_params.append(category_id)
            ans_query += (
                " ORDER BY l.category_id ASC, l.sort_order ASC, ua.answered_at ASC"
            )

            cursor.execute(ans_query, ans_params)
            ans_rows = cursor.fetchall()

            for row in ans_rows:
                d = dict(row)
                lid = d["lesson_id"]
                if lid in lessons_map:
                    lessons_map[lid].answers.append(
                        UserAnswerDetail(
                            id=d["id"],
                            question_text=d["question_text"],
                            user_answer_text=d["user_answer_text"],
                            correct_answer_text=d["correct_answer_text"],
                            is_correct=bool(d["is_correct"]),
                            answered_at=d["answered_at"],
                        )
                    )

            # Сортируем итоговый список по категории и порядку уроков
            return sorted(
                lessons_map.values(), key=lambda x: (x.category_id, x.sort_order)
            )
        finally:
            conn.close()


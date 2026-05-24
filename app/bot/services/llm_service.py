import re
import html
from typing import List, Dict, Tuple
from app.bot.llm.base import BaseLLMClient


class LLMService:
    TG_MAX_LENGTH = 4000
    MAX_HISTORY = 12

    @staticmethod
    def get_prompt(mode: str, context: dict) -> str:
        if mode == "general":
            return "Ты — опытный эксперт преподаватель по программированию на Python. Отвечай четко, по делу, на русском языке. Помогай пользователю все что он попросит по темам программирования."

        elif mode == "category_helper":
            cats = context.get("categories", [])
            cat_list = "\n".join([f"- {c.name}" for c in cats])
            return f"""Ты — помощник по выбору учебного курса.
Доступные категории:
{cat_list}
Твоя задача: кратко расспросить пользователя о его целях, уровне знаний и интересах, чтобы рекомендовать одну из категорий. Отвечай на русском, коротко (1-3 предложения). Не выдумывай категории."""

        elif mode == "lesson_qa":
            # 1. Очищаем HTML и обрезаем контент урока, чтобы не превысить лимит токенов
            raw_content = context.get("lesson_content", "")
            clean_content = re.sub(r"<[^>]+>", "", raw_content)
            clean_content = (
                clean_content.replace("&lt;", "<")
                .replace("&gt;", ">")
                .replace("&quot;", '"')
                .replace("&amp;", "&")
                .strip()
            )
            if len(clean_content) > 1200:
                clean_content = (
                    clean_content[:1200]
                    + "\n... (материал обрезан для экономии контекста)"
                )

            quiz_ctx = context.get("quiz_context")
            parts = []

            # 2. КОНТЕКСТ ВОПРОСА ПЕРВЫМ (чтобы точно не обрезался при лимите токенов)
            if quiz_ctx:
                q_text = quiz_ctx.get("question", "")
                u_ans = quiz_ctx.get("user_answer", "")
                c_ans = quiz_ctx.get("correct_answer", "")
                status = "верный" if quiz_ctx.get("is_correct") else "неверный"
                parts.append(f"""[КОНТЕКСТ ТЕКУЩЕГО ВОПРОСА]
Вопрос теста: «{q_text}»
Ответ ученика: «{u_ans}» ({status})
Правильный ответ: «{c_ans}»

ИНСТРУКЦИЯ:
1. Сразу начни с разбора этого ответа. Объясни, почему он {status}.
2. Если ответ неверный — четко объясни ошибку, разбери логику и почему правильный ответ именно такой.
3. Если верный — похвали и кратко углуби тему или дай интересный факт.
4. НЕ спрашивай «чем помочь?» или «что объяснить?». Сразу давай разбор. После этого поддерживай диалог по теме урока.""")

            # 3. Роль и материал урока
            parts.append(f"""Ты — преподаватель по теме урока «{context.get("lesson_title", "")}».
Содержание урока (справочно):
{clean_content}

Отвечай на вопросы ученика строго по этой теме. Кратко, на русском. Без markdown.""")

            return "\n\n".join(parts)

        elif mode == "interview":
            return f"""Ты — технический интервьюер. Проведи собеседование по теме «{context.get("lesson_title", "")}».
Задавай по одному вопросу за раз. Жди ответа. Оценивай кратко. Если ответ слабый, давай наводящую подсказку. Собеседование на русском. Без markdown."""

        return "Ты — полезный ассистент."

    @classmethod
    def trim_history(cls, history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if len(history) <= cls.MAX_HISTORY:
            return history
        return [history[0]] + history[-(cls.MAX_HISTORY - 1) :]

    @classmethod
    def split_text(cls, text: str) -> list[str]:
        if len(text) <= cls.TG_MAX_LENGTH:
            return [text]
        chunks = []
        while text:
            chunks.append(text[: cls.TG_MAX_LENGTH])
            text = text[cls.TG_MAX_LENGTH :]
        return chunks

    @classmethod
    async def ask(
        cls, llm: BaseLLMClient, history: List[Dict[str, str]]
    ) -> Tuple[str, List[Dict[str, str]]]:
        history = cls.trim_history(history)
        reply = await llm.chat(history)
        history.append({"role": "assistant", "content": reply})
        return html.escape(reply), history

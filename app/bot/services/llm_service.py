import html
from typing import List, Dict, Tuple
from app.bot.llm.base import BaseLLMClient


class LLMService:
    TG_MAX_LENGTH = 4000
    MAX_HISTORY = 12

    @staticmethod
    def get_prompt(mode: str, context: dict) -> str:
        if mode == "general":
            return "Ты — опытный эксперт по программированию. Отвечай четко, по делу, на русском языке. Помогай пользователю все что он попросит по темам программирования."
        elif mode == "category_helper":
            cats = context.get("categories", [])
            cat_list = "\n".join([f"- {c.name}" for c in cats])
            return f"""Ты — помощник по выбору учебного курса.
Доступные категории:
{cat_list}
Твоя задача: кратко расспросить пользователя о его целях, уровне знаний и интересах, чтобы рекомендовать одну из категорий. Отвечай на русском, коротко (1-3 предложения). Не выдумывай категории."""
        elif mode == "lesson_qa":
            return f"""Ты — преподаватель по теме урока «{context.get("lesson_title", "")}».
Содержание: {context.get("lesson_content", "")}
Отвечай на вопросы ученика строго по этой теме. Кратко, на русском. Без markdown."""
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

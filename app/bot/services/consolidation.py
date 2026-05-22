import html
from typing import List, Dict
from app.bot.llm.base import BaseLLMClient


class ConsolidationService:
    """Сервис для логики закрепления материала."""

    TG_MAX_LENGTH = 4000

    @staticmethod
    def build_system_prompt(lesson_title: str, lesson_content: str) -> str:
        return f"""Ты — дружелюбный преподаватель-репетитор. Ты помогаешь ученику закрепить тему урока.
ТЕКУЩИЙ УРОК: «{lesson_title}»
СОДЕРЖАНИЕ УРОКА:
{lesson_content}

ПРАВИЛА ПОВЕДЕНИЯ (СТРОГО СОБЛЮДАЙ):
1. Отвечай ТОЛЬКО на русском языке.
2. Начни с одного конкретного вопроса по теме урока.
3. НЕ давай готовый ответ в своём вопросе.
4. Отвечай коротко — 1-3 предложения за реплику.
5. Не используй markdown-разметку, пиши простым текстом.
Начни диалог с приветствия и первого вопроса."""

    @staticmethod
    def trim_history(
        history: List[Dict[str, str]], max_messages: int = 12
    ) -> List[Dict[str, str]]:
        if len(history) <= max_messages:
            return history
        return [history[0]] + history[-(max_messages - 1) :]

    @classmethod
    def split_text(cls, text: str) -> list[str]:
        """Безопасно разбивает текст на части для Telegram."""
        if len(text) <= cls.TG_MAX_LENGTH:
            return [text]
        chunks = []
        while text:
            chunks.append(text[: cls.TG_MAX_LENGTH])
            text = text[cls.TG_MAX_LENGTH :]
        return chunks

    @classmethod
    async def ask_llm(
        cls, llm: BaseLLMClient, history: List[Dict[str, str]]
    ) -> tuple[str, List[Dict[str, str]]]:
        """Отправляет запрос, обрезает историю и возвращает безопасный для HTML ответ."""
        history = cls.trim_history(history)
        reply = await llm.chat(history)
        history.append({"role": "assistant", "content": reply})

        # Экранируем HTML, чтобы не сломать parse_mode="HTML"
        safe_reply = html.escape(reply)
        return safe_reply, history

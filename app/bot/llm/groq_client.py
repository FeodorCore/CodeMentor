import logging
from typing import List, Dict
from groq import AsyncGroq, GroqError
from .base import BaseLLMClient

logger = logging.getLogger(__name__)


class GroqClient(BaseLLMClient):
    def __init__(self, api_key: str, model: str, timeout: float = 90.0):
        self.model = model
        # Используем асинхронный клиент Groq
        self.client = AsyncGroq(api_key=api_key, timeout=timeout)

    async def chat(self, history: List[Dict[str, str]]) -> str:
        try:
            chat_completion = await self.client.chat.completions.create(
                messages=history,
                model=self.model,
                temperature=0.7,
                max_tokens=1024,
            )
            content = chat_completion.choices[0].message.content
            return content.strip() if content else "⚠️ Пустой ответ от Groq."
        except GroqError as e:
            logger.error(f"Ошибка API Groq: {e}")
            return "❌ Ошибка сервера нейросети (Groq). Попробуйте позже."
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка Groq: {e}")
            return "❌ Внутренняя ошибка при общении с нейросетью."

    async def close(self):
        await self.client.close()

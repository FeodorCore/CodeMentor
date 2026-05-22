import httpx
import logging
from typing import List, Dict
from app.bot.llm.base import BaseLLMClient

logger = logging.getLogger(__name__)


class OllamaClient(BaseLLMClient):
    def __init__(self, base_url: str, model: str, timeout: float = 200.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def chat(self, history: List[Dict[str, str]]) -> str:
        client = await self._get_client()
        payload = {
            "model": self.model,
            "messages": history,
            "stream": False,
            "think": False,
        }
        try:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            return (
                data.get("message", {}).get("content", "").strip() or "⚠️ Пустой ответ."
            )

        except httpx.ConnectError:
            logger.error("Не удалось подключиться к Ollama (сервис не запущен).")
            return "⚠️ Ollama недоступна. Убедитесь, что сервис запущен."

        except httpx.HTTPStatusError as e:
            # Специальная обработка для 404 (Модель не найдена)
            if e.response.status_code == 404:
                logger.error(
                    f"Модель '{self.model}' не найдена в Ollama. Ответ: {e.response.text}"
                )
                return f"❌ <b>Ошибка Ollama:</b> Модель <code>{self.model}</code> не найдена.\n\n<i>Выполните в терминале:</i>\n<code>ollama pull {self.model}</code>"

            logger.error(
                f"Ollama HTTP ошибка: {e.response.status_code} - {e.response.text}"
            )
            return f"❌ Ошибка сервера Ollama (HTTP {e.response.status_code})."

        except httpx.TimeoutException:
            logger.error("Таймаут запроса к Ollama.")
            return "⏳ Ollama думает слишком долго. Попробуйте позже."

        except Exception as e:
            logger.exception(f"Непредвиденная ошибка Ollama: {e}")
            return "❌ Внутренняя ошибка при общении с Ollama."

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

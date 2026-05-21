import httpx
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class OllamaClient:
    """Асинхронный клиент для работы с Ollama API."""
    def __init__(self, base_url: str, model: str, timeout: float = 90.0):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def chat(self, history: List[Dict[str, str]]) -> str:
        """Отправляет историю в Ollama и возвращает ответ ассистента."""
        client = await self._get_client()
        payload = {
            "model": self.model,
            "messages": history,
            "stream": False
        }
        try:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")
            return content.strip() if content else "⚠️ Пустой ответ от модели."
        except httpx.ConnectError:
            logger.error("Не удалось подключиться к Ollama. Проверьте, запущен ли сервис.")
            return "⚠️ Нейросеть временно недоступна. Убедитесь, что Ollama запущена, и попробуйте позже."
        except httpx.TimeoutException:
            logger.error("Превышено время ожидания ответа от Ollama.")
            return "⏳ Нейросеть думает слишком долго. Попробуйте упростить вопрос или повторить позже."
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama вернула ошибку HTTP: {e.response.status_code} - {e.response.text}")
            return f"❌ Ошибка сервера нейросети (HTTP {e.response.status_code})."
        except Exception as e:
            logger.exception(f"Непредвиденная ошибка при запросе к Ollama: {e}")
            return "❌ Произошла внутренняя ошибка при общении с нейросетью."

    @staticmethod
    def trim_history(history: List[Dict[str, str]], max_messages: int = 12) -> List[Dict[str, str]]:
        """
        Ограничивает длину истории, чтобы не превысить контекстное окно модели.
        Сохраняет системный промпт (первый элемент) и последние N сообщений.
        """
        if len(history) <= max_messages:
            return history
        return [history[0]] + history[-(max_messages - 1):]
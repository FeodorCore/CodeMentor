from abc import ABC, abstractmethod
from typing import List, Dict


class BaseLLMClient(ABC):
    """Базовый класс для всех LLM провайдеров."""

    @abstractmethod
    async def chat(self, history: List[Dict[str, str]]) -> str:
        pass

    @abstractmethod
    async def close(self):
        pass

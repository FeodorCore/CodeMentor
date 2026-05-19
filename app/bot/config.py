import os
from dotenv import load_dotenv
from dataclasses import dataclass
load_dotenv()

@dataclass
class BotConfig:
    """Конфигурация бота."""
    token: str
    api_base_url: str


def load_config() -> BotConfig:
    """Загрузка конфига из переменных окружения."""
    token = os.getenv("BOT_TOKEN", "")
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")

    if not token:
        raise ValueError("BOT_TOKEN не установлен в переменных окружения!")

    return BotConfig(token=token, api_base_url=api_url.rstrip("/"))
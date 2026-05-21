import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()

@dataclass
class BotConfig:
    """Конфигурация бота."""
    token: str
    api_base_url: str
    ollama_base_url: str
    ollama_model: str

def load_config() -> BotConfig:
    """Загрузка конфига из переменных окружения."""
    token = os.getenv("BOT_TOKEN", "")
    api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3")

    if not token:
        raise ValueError("BOT_TOKEN не установлен в переменных окружения!")

    return BotConfig(
        token=token,
        api_base_url=api_url.rstrip("/"),
        ollama_base_url=ollama_url.rstrip("/"),
        ollama_model=ollama_model
    )
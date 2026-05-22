from app.bot.config import BotConfig
from app.bot.llm.base import BaseLLMClient
from app.bot.llm.ollama_client import OllamaClient
from app.bot.llm.groq_client import GroqClient


def create_llm_client(config: BotConfig) -> BaseLLMClient:
    if config.llm_provider == "groq":
        if not config.groq_api_key:
            raise ValueError("GROQ_API_KEY не установлен!")
        return GroqClient(api_key=config.groq_api_key, model=config.llm_model)

    return OllamaClient(base_url=config.ollama_base_url, model=config.llm_model)

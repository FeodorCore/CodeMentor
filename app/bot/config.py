import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class BotConfig:
    token: str
    api_base_url: str
    llm_provider: str  # "ollama" или "groq"
    llm_model: str
    ollama_base_url: str
    groq_api_key: str


def load_config() -> BotConfig:
    return BotConfig(
        token=os.getenv("BOT_TOKEN", ""),
        api_base_url=os.getenv("API_BASE_URL", "http://localhost:8000"),
        llm_provider=os.getenv("LLM_PROVIDER", "groq").lower(),
        llm_model=os.getenv("LLM_MODEL", "llama3-8b-8192"),
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        groq_api_key=os.getenv("GROQ_API_KEY", ""),
    )

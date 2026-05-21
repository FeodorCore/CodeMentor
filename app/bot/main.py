import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.bot.config import load_config
from app.bot.api_client import ApiClient
from app.bot.llm_service import OllamaClient
from app.bot.handlers import all_routers


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    config = load_config()
    logger.info(f"API URL: {config.api_base_url}")
    logger.info(f"Ollama URL: {config.ollama_base_url} | Model: {config.ollama_model}")

    bot: Bot = Bot(token=config.token)
    dp = Dispatcher(storage=MemoryStorage())

    api_client = ApiClient(base_url=config.api_base_url)
    ollama_client = OllamaClient(
        base_url=config.ollama_base_url, model=config.ollama_model
    )

    dp.include_router(all_routers)
    dp.workflow_data.update({"api": api_client, "ollama": ollama_client})

    try:
        logger.info("Бот запущен!")
        await dp.start_polling(bot)
    finally:
        await ollama_client.close()
        await api_client.close()
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    asyncio.run(main())

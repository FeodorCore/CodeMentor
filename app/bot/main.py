import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.config import load_config
from app.bot.api_client import ApiClient
from app.bot.handlers import all_routers
from app.bot.llm.factory import create_llm_client
from app.bot.services.consolidation import ConsolidationService


async def main():
    # 1. Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    # 2. Загрузка конфигурации
    config = load_config()
    logger.info(f"API URL: {config.api_base_url}")
    logger.info(
        f"LLM Provider: {config.llm_provider.upper()} | Model: {config.llm_model}"
    )

    # 3. Инициализация бота и диспетчера
    bot = Bot(token=config.token)
    dp = Dispatcher(storage=MemoryStorage())

    # 4. Инициализация сервисов и клиентов (Dependency Injection)
    api_client = ApiClient(base_url=config.api_base_url)
    llm_client = create_llm_client(config)
    consolidation_svc = ConsolidationService()

    # 5. Регистрация роутеров
    dp.include_router(all_routers)

    # 6. Проброс зависимостей в handlers (workflow_data)
    dp.workflow_data.update(
        {
            "api": api_client,
            "llm": llm_client,
            "consolidation": consolidation_svc,
        }
    )

    # 7. Запуск polling
    try:
        logger.info("🤖 Бот успешно запущен!")
        await dp.start_polling(bot)
    finally:
        # 8. Корректное закрытие всех соединений при остановке
        logger.info("Завершение работы и закрытие соединений...")
        await llm_client.close()
        await api_client.close()
        await bot.session.close()
        logger.info("🛑 Бот остановлен.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен пользователем (Ctrl+C).")

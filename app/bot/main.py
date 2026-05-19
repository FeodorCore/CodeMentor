import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.bot.config import load_config
from app.bot.api_client import ApiClient
from app.bot.handlers import all_routers


async def main():
    """Запуск бота."""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    # Загрузка конфигурации
    config = load_config()
    logger.info(f"API URL: {config.api_base_url}")

    # Инициализация бота и диспетчера
    bot = Bot(token=config.token)
    dp = Dispatcher(storage=MemoryStorage())

    # Инициализация API-клиента
    api_client = ApiClient(base_url=config.api_base_url)

    # Регистрируем роутеры
    dp.include_router(all_routers)

    # Пробрасываем api_client в handlers через middleware
    # (aiogram 3.x позволяет передавать kwargs в update)
    dp.workflow_data.update({"api": api_client})

    try:
        logger.info("Бот запущен!")
        await dp.start_polling(bot)
    finally:
        await api_client.close()
        await bot.session.close()
        logger.info("Бот остановлен.")


if __name__ == "__main__":
    asyncio.run(main())
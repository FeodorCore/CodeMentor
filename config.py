import os
from dotenv import load_dotenv

load_dotenv()  # загружает переменные из файла .env

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "education_bot.db")

# API KEY для защиты эндпоинтов бэкенда
API_KEY = "supersecret-api-key-2025"   # измени на свой!

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")  # получите токен у @BotFather
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан в переменных окружения или .env")

# URL бэкенда (где запущен FastAPI)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
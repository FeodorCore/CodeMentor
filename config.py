import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "education_bot.db")

# API KEY для защиты эндпоинтов бэкенда
API_KEY = "supersecret-api-key-2025"

# Настройки бота
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не задан")

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Настройки админки
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "your-session-secret-key-change-it")
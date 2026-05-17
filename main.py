from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from config import SESSION_SECRET_KEY
from routers import articles, users, quiz, mailing, admin

app = FastAPI(title="Education Bot API", version="1.0")

# Добавляем middleware для сессий
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

# Подключаем роутеры
app.include_router(articles.router)
app.include_router(users.router)
app.include_router(quiz.router)
app.include_router(mailing.router)
app.include_router(admin.router)

@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "API is running"}
from fastapi import FastAPI
from routers import articles, users, quiz, mailing

app = FastAPI(title="Education Bot API", version="1.0")

# подключаем роутеры
app.include_router(articles.router)
app.include_router(users.router)
app.include_router(quiz.router)
app.include_router(mailing.router)

@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "API is running"}
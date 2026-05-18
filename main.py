# main.py
from fastapi import FastAPI
from app.api.admin.__init__ import router as admin_router
from app.core.database import DatabaseManager
from contextlib import asynccontextmanager

@asynccontextmanager
async def startup_event(app: FastAPI):
    db_manager = DatabaseManager(db_name="app.db", schema_name="schema.sql")
    db_manager.create_or_skip()
    yield
app = FastAPI(title="Simple Admin API", lifespan=startup_event)

app.include_router(admin_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.routes.auth import router as auth_router


app = FastAPI(
    title="Yuz-Tut-Backend",
    description="Backend API for Yuz-Tut",
    version="1.0.0",
    )

@app.get("/")
def message():
    return {"Yuz Tut": "Backend"}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/database")
async def database_health_check(db: AsyncSession = Depends(get_db)):

    await db.execute(text("SELECT 1"))

    return {
        "status": "ok",
        "database": "connected"
    }
app.include_router(auth_router)
from contextlib import asynccontextmanager
from fastapi import FastAPI

import uvicorn

from core.config import settings
from api import router as api_router  # Импорт основного роутера API v1


app = FastAPI(
    title="Faceit Competitive Rating Service"
)
app.include_router(api_router)


if __name__ == "__main__":  # Точка входа для запуска приложения
    uvicorn.run("main:app", reload=True)

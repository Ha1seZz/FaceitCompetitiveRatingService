from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api import router as api_router
from app.api.exception_handlers import setup_exception_handlers
from app.api.middleware import LoggingMiddleware
from app.core.logger import setup_logging
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    from loguru import logger
    logger.info("Starting up FaceitCompetitiveRatingService...")

    limits = httpx.Limits(max_keepalive_connections=20, max_connections=100)
    app.state.httpx_client = httpx.AsyncClient(
        base_url=settings.faceit.base_url,
        headers={"Authorization": f"Bearer {settings.faceit.api_key}"},
        limits=limits,
        timeout=httpx.Timeout(10.0),
    )

    logger.info(
        "HTTPX client initialized | base_url={base_url} | pool_size={pool_size}",
        base_url=settings.faceit.base_url,
        pool_size=limits.max_connections,
    )

    yield

    await app.state.httpx_client.aclose()
    logger.info("HTTPX client closed. Shutdown complete.")


app = FastAPI(
    title="Faceit Competitive Rating Service",
    lifespan=lifespan,
)

app.add_middleware(LoggingMiddleware)

setup_exception_handlers(app)

app.include_router(api_router)


@app.exception_handler(httpx.HTTPStatusError)
async def httpx_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
    """Глобальный обработчик ошибок HTTP-статусов для клиента httpx."""
    return JSONResponse(
        status_code=exc.response.status_code,
        content={"detail": f"External API error: {exc.response.text}"},
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)

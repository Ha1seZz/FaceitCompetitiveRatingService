from contextlib import asynccontextmanager

import httpx
import uvicorn
from loguru import logger
from fastapi import FastAPI, Request
from fastapi_cache import FastAPICache
from fastapi.responses import JSONResponse
from fastapi_cache.backends.redis import RedisBackend
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from redis import asyncio as aioredis

from app.core.settings import db_helper
from app.api import router as api_router
from app.api.exception_handlers import setup_exception_handlers
from app.api.middleware import ASGIRequestLoggerMiddleware
from app.core.config import settings
from app.core.limiter import limiter
from app.core.logger import setup_logging

redis_client: aioredis.Redis | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    setup_logging()
    logger.info("Starting up FaceitCompetitiveRatingService...")

    try:
        await db_helper.ping()
        logger.info("Database pool warmed up successfully.")
    except Exception as e:
        logger.critical(
            "Infrastructure check failed. Database is unreachable: {error}",
            error=e,
        )
        raise

    try:
        redis_client = aioredis.from_url(
            settings.redis.url,
            encoding="utf8",
            decode_responses=True,
        )
        FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")
        logger.info("Redis client initialized successfully.")
    except Exception as e:
        logger.critical(
            "Infrastructure check failed. Redis is unreachable: {error}",
            error=e,
        )
        raise

    try:
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
    except Exception as e:
        logger.critical(
            "Infrastructure check failed. HTTPX client initialization failed: {error}",
            error=e,
        )
        raise

    yield

    await db_helper.engine.dispose()
    logger.info("Database pool disposed. Shutdown complete.")

    await redis_client.close()
    logger.info("Redis client closed. Shutdown complete.")

    await app.state.httpx_client.aclose()
    logger.info("HTTPX client closed. Shutdown complete.")


app = FastAPI(
    title="Faceit Competitive Rating Service",
    lifespan=lifespan,
)

app.state.limiter = limiter

app.add_middleware(ASGIRequestLoggerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
    allow_credentials=settings.cors.allow_credentials,
)
app.add_middleware(SlowAPIMiddleware)

setup_exception_handlers(app)

app.include_router(api_router)


@app.exception_handler(httpx.HTTPStatusError)
async def httpx_status_error_handler(request: Request, exc: httpx.HTTPStatusError):
    """Глобальный обработчик ошибок HTTP-статусов для клиента httpx."""

    logger.error(
        "External API error | method={method} | url={url} | status={status} | body={body}",
        method=exc.request.method,
        url=str(exc.request.url),
        status=exc.response.status_code,
        body=exc.response.text,
    )

    return JSONResponse(
        status_code=exc.response.status_code,
        content={"detail": f"External API error. Please try again later."},
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=settings.debug, access_log=False)

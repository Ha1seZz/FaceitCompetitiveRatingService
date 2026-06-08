"""Модуль промежуточного ПО (Middleware) для логирования и трассировки запросов."""

import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from loguru import logger

request_id_context_var: ContextVar[str] = ContextVar("request_id", default="system")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Промежуточное ПО для логирования жизненного цикла HTTP-запросов."""

    async def dispatch(self, request: Request, call_next):
        """Перехватывает HTTP-запрос, логирует его этапы и замеряет время выполнения."""

        req_id = str(uuid.uuid4())[:8]
        token = request_id_context_var.set(req_id)

        with logger.contextualize(request_id=req_id):
            logger.info(f"Входящий запрос: {request.method} {request.url.path}")
            start_time = time.time()

            try:
                response = await call_next(request)
                process_time = (time.time() - start_time) * 1000
                logger.info(
                    f"Запрос завершен: {request.method} {request.url.path} - "
                    f"Статус: {response.status_code} - Время: {process_time:.2f}ms"
                )

                response.headers["X-Request-ID"] = req_id
                return response

            except Exception as e:
                process_time = (time.time() - start_time) * 1000
                logger.exception(
                    f"ОШИБКА 500: {request.method} {request.url.path} - "
                    f"Время: {process_time:.2f}ms. Причина: {e}"
                )
                raise

            finally:
                request_id_context_var.reset(token)

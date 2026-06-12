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

        start_time = time.time()

        with logger.contextualize(request_id=req_id):
            try:
                response = await call_next(request)
                process_time = (time.time() - start_time) * 1000
                logger.info(
                    "Запрос завершен: {method} {path} - "
                    "Статус: {status_code} - Время: {process_time:.2f}ms",
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    process_time=process_time,
                )

                response.headers["X-Request-ID"] = req_id
                return response

            except Exception as e:
                process_time = (time.time() - start_time) * 1000
                logger.exception(
                    "Ошибка при обработке запроса: {method} {path} - "
                    "Время: {process_time:.2f}ms. Причина: {reason}",
                    method=request.method,
                    path=request.url.path,
                    process_time=process_time,
                    reason=str(e),
                )
                raise

            finally:
                request_id_context_var.reset(token)

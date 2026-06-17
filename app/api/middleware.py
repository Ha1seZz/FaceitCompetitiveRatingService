"""Модуль промежуточного ПО (Middleware) для логирования и трассировки запросов."""

import time
import uuid
from contextvars import ContextVar

from starlette.types import ASGIApp, Scope, Receive, Send
from loguru import logger

request_id_context_var: ContextVar[str] = ContextVar("request_id", default="system")


class ASGIRequestLoggerMiddleware:
    """Низкоуровневое ASGI-middleware для логирования запросов без буферизации."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        """Перехватывает запрос на уровне ASGI, логирует результат одной строкой."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        req_id = str(uuid.uuid4())[:8]
        token = request_id_context_var.set(req_id)
        start_time = time.time()

        status_code_container = [500]
        response_time = [None]

        async def send_wrapper(message: dict):
            """Перехватывает отправку сообщений клиенту для извлечения статус-кода."""
            if message["type"] == "http.response.start":
                status_code_container[0] = message["status"]

            if message["type"] == "http.response.body" and response_time[0] is None:
                response_time[0] = (time.time() - start_time) * 1000

            await send(message)

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "UNKNOWN")
        query_string = scope.get("query_string", b"").decode("utf-8")
        full_path = f"{path}?{query_string}" if query_string else path

        with logger.contextualize(request_id=req_id):
            try:
                await self.app(scope, receive, send_wrapper)
                total_time = (time.time() - start_time) * 1000
                resp_time = response_time[0] or total_time

                logger.info(
                    "Запрос завершен: {method} {path} - "
                    "Статус: {status_code} - Ответ клиенту: {resp_time:.2f}ms (Всего с фоном: {total_time:.2f}ms)",
                    method=method,
                    path=full_path,
                    status_code=status_code_container[0],
                    resp_time=resp_time,
                    total_time=total_time,
                )

            except Exception as e:
                total_time = (time.time() - start_time) * 1000
                logger.exception(
                    "Ошибка при обработке запроса: {method} {path} - "
                    "Время: {total_time:.2f}ms. Причина: {reason}",
                    method=method,
                    path=path,
                    total_time=total_time,
                    reason=str(e),
                )
                raise

            finally:
                request_id_context_var.reset(token)

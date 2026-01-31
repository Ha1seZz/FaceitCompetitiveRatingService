"""Кастомные исключения приложения."""


class ApplicationException(Exception):
    """Базовое исключение приложения, от которого наследуются все кастомные ошибки."""

    def __init__(self, message: str = "Application error"):
        self.message = message
        super().__init__(self.message)


class FaceitEntityNotFound(ApplicationException):
    """Исключение, выбрасываемое, когда сущность (игрок, матч) не найдена в Faceit API."""

    def __init__(self, message: str = "Entity not found on Faceit"):
        super().__init__(message)


class ExternalServiceUnavailable(ApplicationException):
    """Исключение, выбрасываемое при временной недоступности внешнего сервиса (HTTP 5xx)."""

    def __init__(self, message: str = "External service is unavailable"):
        super().__init__(message)

"""Кастомные исключения приложения."""


class ApplicationException(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str = "Application error"):
        self.message = message
        super().__init__(self.message)


class FaceitEntityNotFound(ApplicationException):
    """Сущность не найдена в Faceit API."""

    def __init__(self, message: str = "Entity not found on Faceit"):
        super().__init__(message)


class ExternalServiceUnavailable(ApplicationException):
    """Внешний сервис недоступен."""

    def __init__(self, message: str = "External service is unavailable"):
        super().__init__(message)

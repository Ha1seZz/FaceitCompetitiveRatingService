"""Кастомные исключения приложения."""


class ApplicationException(Exception):
    """Базовое исключение приложения, от которого наследуются все кастомные ошибки."""

    def __init__(self, message: str = "Application error"):
        super().__init__(message)


class FaceitEntityNotFound(ApplicationException):
    """Исключение, выбрасываемое, когда сущность (игрок, матч) не найдена в Faceit API."""

    def __init__(self, message: str = "Entity not found on Faceit"):
        super().__init__(message)


class ExternalServiceUnavailable(ApplicationException):
    """Исключение, выбрасываемое при временной недоступности внешнего сервиса (HTTP 5xx)."""

    def __init__(self, message: str = "External service is unavailable"):
        super().__init__(message)


class InsufficientDataError(ApplicationException):
    """Исключение, выбрасываемое, когда данных недостаточно для выполнения анализа."""

    def __init__(self, message: str = "Not enough data for analysis"):
        super().__init__(message)


class PlayerError(Exception):
    """Базовое исключение домена игроков."""

    pass


class PlayerNotFoundError(PlayerError):
    """Исключение, выбрасываемое, если игрок не найден в системе."""

    def __init__(self, player_id: str):
        self.player_id = player_id
        super().__init__(f"Player with ID {player_id} not found.")


class QueueServiceUnavailableError(Exception):
    """Вызывается, когда сервис очередей (ARQ/Redis) недоступен или не смог принять задачу."""

    def __init__(self, message: str = "Фоновая очередь задач недоступна"):
        super().__init__(message)


class ResourceLockedError(Exception):
    """
    Исключение, выбрасываемое при попытке доступа к ресурсу,
    который в данный момент обновляется или заблокирован другим процессом.
    """

    def __init__(
        self,
        message: str = "Ресурс временно заблокирован. Повторите попытку позже.",
    ):
        super().__init__(message)

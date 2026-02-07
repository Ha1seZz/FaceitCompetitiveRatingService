"""Конфигурация приложения."""

from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent.parent


class ApiV1Prefix(BaseModel):
    """Настройки префикса для первой версии API."""

    prefix: str = "/v1"
    players: str = "/players"
    matches: str = "/matches"


class ApiPrefix(BaseModel):
    """Глобальная структура путей API проекта."""

    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class DbSettings(BaseModel):
    """Настройки подключения к базе данных PostgreSQL."""

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "password"
    name: str = "database"
    echo: bool = False

    @property
    def url(self) -> str:
        """Формирует DSN строку для SQLAlchemy (asyncpg)."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class FaceitSettings(BaseModel):
    """Конфигурация для авторизации и запросов к Faceit Data API."""

    api_key: str = "placeholder"
    base_url: str = "https://open.faceit.com/data/v4"
    default_language: str = "ru"


class PlayerSettings(BaseModel):
    """Настройки бизнес-логики обработки данных игрока."""

    min_matches_for_analysis: int = 10


class Settings(BaseSettings):
    """
    Глобальный контейнер настроек приложения.

    Автоматически подтягивает значения из системных переменных окружения
    или .env файла. Поддерживает вложенные настройки через разделитель '__'.
    """

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )
    api: ApiPrefix = ApiPrefix()
    db: DbSettings = DbSettings()
    faceit: FaceitSettings = FaceitSettings()
    player: PlayerSettings = PlayerSettings()


# Глобальный экземпляр настроек для использования в приложении
settings = Settings()

from pathlib import Path
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent.parent  # Определяем путь к корневой директории проекта


class DbSettings(BaseModel):
    """
    Схема настроек базы данных.
    """
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "password"
    name: str = "database"
    echo: bool = False

    @property
    def database_url(self) -> str:
        """
        Собирает DSN строку для SQLAlchemy (asyncpg).
        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


class FaceitSettings(BaseModel):
    api_key: str = "placeholder"
    base_url: str = "https://open.faceit.com/data/v4"


class Settings(BaseSettings):
    """
    Основной класс настроек приложения. Наследуется от BaseSettings,
    что дает возможность автоматически читать данные из переменных окружения и .env файлов.
    """
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__"
    )

    api_v1_prefix: str = "/api/v1"

    db: DbSettings = DbSettings()

    faceit: FaceitSettings = FaceitSettings()


settings = Settings()

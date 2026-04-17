from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"

class Settings(BaseSettings):
    DATABASE_URL: str
    TELEGRAM_BOT_TOKEN: str | None = None
    TELEGRAM_API_ID: str | None = None
    TELEGRAM_API_HASH: str | None = None
    TELEGRAM_SESSION_NAME: str | None = None
    YANDEX_FOLDER_ID: str | None = None
    YANDEX_API_KEY: str | None = None
    VK_APP_ID : str | None = None 
    VK_TOKEN : str | None = None

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
    )

settings = Settings()
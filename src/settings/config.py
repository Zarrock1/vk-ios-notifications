import sys
from typing import Literal
from urllib.parse import urlsplit

from loguru import logger
from pydantic import ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    VK_TOKEN: str
    BARK_TOKEN: str
    BARK_URL: str = "https://api.day.app"
    BARK_SOUND: str | None = None
    BARK_LEVEL: Literal["active", "timeSensitive", "passive", "critical"] | None = None
    BARK_GROUP_BY_DIALOG: bool = True
    READ_CHECK_DELAY: float = 2
    NOTIFY_STARTUP: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @model_validator(mode="after")
    def _normalize_bark(self) -> "Settings":
        # Из приложения Bark удобно копировать ссылку целиком: https://api.day.app/KEY/
        token = self.BARK_TOKEN.strip().strip("/")
        if token.startswith(("http://", "https://")):
            parts = urlsplit(token)
            path, _, token = parts.path.rstrip("/").rpartition("/")
            self.BARK_URL = f"{parts.scheme}://{parts.netloc}{path}"
        self.BARK_TOKEN = token
        self.BARK_URL = self.BARK_URL.strip().rstrip("/")
        self.VK_TOKEN = self.VK_TOKEN.strip()
        return self


try:
    settings = Settings()
except ValidationError as error:
    logger.critical(
        "Некорректная конфигурация: заполните .env (см. sample.env) "
        f"или передайте переменные окружения.\n{error}",
    )
    sys.exit(1)

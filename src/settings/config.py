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
        # Из приложения Bark удобно копировать ссылку целиком, в том числе пример
        # вида https://api.day.app/KEY/title/body?group=... — ключ идёт первым в пути
        token = self.BARK_TOKEN.strip()
        if token.startswith(("http://", "https://")):
            parts = urlsplit(token)
            segments = [segment for segment in parts.path.split("/") if segment]
            token = segments[0] if segments else ""
            self.BARK_URL = f"{parts.scheme}://{parts.netloc}"
        self.BARK_TOKEN = token.strip("/")
        self.BARK_URL = self.BARK_URL.strip().rstrip("/")
        # Токен можно вставить вместе с адресной строкой: https://oauth.vk.com/blank.html#access_token=...&expires_in=0
        vk_token = self.VK_TOKEN.strip()
        if "access_token=" in vk_token:
            vk_token = vk_token.split("access_token=", 1)[1].split("&", 1)[0]
        self.VK_TOKEN = vk_token
        return self


try:
    settings = Settings()
except ValidationError as error:
    logger.critical(
        "Некорректная конфигурация: заполните .env (см. sample.env) "
        f"или передайте переменные окружения.\n{error}",
    )
    sys.exit(1)

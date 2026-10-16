import time

from requests import RequestException, session
from loguru import logger

from src.settings.config import settings
from src.settings.constants import (
    VK_ICON_PNG,
    VK_ME,
    REQUEST_TIMEOUT,
    BARK_MAX_BODY_LENGTH,
    BARK_RETRIES,
)


class Bark():
    def __init__(
        self,
        token: str,
        bark_url: str,
        *,
        sound: str | None = None,
        level: str | None = None,
    ) -> None:
        self._token = token
        self._url = bark_url.rstrip("/")
        self._sound = sound
        self._level = level
        self._session = session()

    def notification(
        self,
        title: str,
        body: str,
        *,
        icon: str = VK_ICON_PNG,
        url: str = VK_ME,
        group: str | None = None,
    ) -> bool:
        if len(body) > BARK_MAX_BODY_LENGTH:
            body = body[:BARK_MAX_BODY_LENGTH - 1] + "…"
        payload = {
            "device_key": self._token,
            "title": title,
            "body": body,
            "icon": icon,
            "url": url,
            "group": group,
            "sound": self._sound,
            "level": self._level,
        }
        payload = {key: value for key, value in payload.items() if value}
        for attempt in range(1, BARK_RETRIES + 1):
            try:
                response = self._session.post(
                    f"{self._url}/push",
                    json=payload,
                    timeout=REQUEST_TIMEOUT,
                )
            except RequestException as error:
                logger.warning(f"Не удалось отправить уведомление в Bark (попытка {attempt}): {error}")
            else:
                try:
                    response_json: dict = response.json()
                except ValueError:
                    response_json = {}
                if response.status_code == 200 and response_json.get("code") == 200:
                    return True
                logger.warning(f"Bark вернул ошибку (попытка {attempt}): {response.status_code} {response.text}")
                # 4xx — неверный ключ устройства или запрос, повтор не поможет
                if 400 <= response.status_code < 500 and response.status_code != 429:
                    break
            if attempt < BARK_RETRIES:
                time.sleep(2 ** attempt)
        logger.error(f"Уведомление не доставлено в Bark: {title}")
        return False


if __name__ == "__main__":
    bark = Bark(token=settings.BARK_TOKEN, bark_url=settings.BARK_URL)
    bark.notification("Test", "Message")

VK_ICON_PNG = "https://pics.freeicons.io/uploads/icons/png/2349032111566470622-512.png"
VK_ME = "https://vk.me/"
VK_IM = "https://vk.com/im?sel="

CHAT_ID_OFFSET: int = 2_000_000_000

AUTH_ERROR_CODES: tuple[int, ...] = (5, 1117)
# Ошибки доступа при подключении к Long Poll: токен есть, но для сообщений не годится
ACCESS_ERROR_CODES: tuple[int, ...] = (7, 15, 27, 28)

ATTACHMENT_NAMES: dict[str, str] = {
    "photo": "Фотография",
    "video": "Видеозапись",
    "video_message": "Видеосообщение",
    "audio": "Аудиозапись",
    "audio_message": "Голосовое сообщение",
    "doc": "Документ",
    "graffiti": "Граффити",
    "link": "Ссылка",
    "market": "Товар",
    "market_album": "Подборка товаров",
    "wall": "Запись на стене",
    "wall_reply": "Комментарий на стене",
    "sticker": "Стикер",
    "gift": "Подарок",
    "poll": "Опрос",
    "call": "Звонок",
    "story": "История",
}
GEO_NAME: str = "Геопозиция"
FORWARDED_NAME: str = "Пересланное сообщение"
REPLY_NAME: str = "Ответ на сообщение"
UNKNOWN_ATTACHMENT_NAME: str = "Вложение"

REQUEST_TIMEOUT: int = 30
LONG_POLL_WAIT: int = 25
RECONNECT_DELAY: int = 5
MAX_RECONNECT_DELAY: int = 300
STABLE_CONNECTION_TIME: int = 60
AUTH_RETRY_DELAY: int = 1800
HANDLER_WORKERS: int = 4

BARK_MAX_BODY_LENGTH: int = 1000
BARK_RETRIES: int = 3

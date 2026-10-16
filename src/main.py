import signal
import sys

from loguru import logger

from src.core.bark import Bark
from src.core.exceptions import VKAPIError
from src.core.vk import VKListener
from src.settings.config import settings


def check(listener: VKListener, bark: Bark) -> bool:
    """Проверяет токен VK и доставку в Bark, не запуская слушатель."""
    ok = True
    try:
        logger.info(f"VK: токен принадлежит пользователю {listener.get_account_name()}")
        listener.get_long_poll_server()
        logger.info("VK: доступ к сообщениям (Long Poll) есть")
    except VKAPIError as error:
        logger.error(f"VK: {error}")
        ok = False
    logger.info(f"Bark: отправляю тестовое уведомление через {settings.BARK_URL}")
    if bark.notification("VK уведомления", "Тестовое уведомление: Bark настроен правильно"):
        logger.info("Bark: уведомление отправлено, проверьте iPhone")
    else:
        ok = False
    return ok


def main() -> None:
    bark = Bark(
        token=settings.BARK_TOKEN,
        bark_url=settings.BARK_URL,
        sound=settings.BARK_SOUND,
        level=settings.BARK_LEVEL,
    )
    listener = VKListener(
        token=settings.VK_TOKEN,
        bark=bark,
        read_check_delay=settings.READ_CHECK_DELAY,
        group_by_dialog=settings.BARK_GROUP_BY_DIALOG,
        notify_startup=settings.NOTIFY_STARTUP,
    )
    if sys.argv[1:] == ["check"]:
        sys.exit(0 if check(listener, bark) else 1)
    # Python в роли PID 1 в контейнере игнорирует SIGTERM — завершаемся сами
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    try:
        listener.listen()
    except KeyboardInterrupt:
        logger.info("Остановлено пользователем")


if __name__ == "__main__":
    main()

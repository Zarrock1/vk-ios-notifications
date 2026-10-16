class VKAPIError(Exception):
    """Ошибка при обращении к VK API."""

    def __init__(self, message: str, code: int | None = None) -> None:
        super().__init__(message)
        self.code = code


class VKAuthError(VKAPIError):
    """Токен VK недействителен или не подходит: переподключение бессмысленно."""

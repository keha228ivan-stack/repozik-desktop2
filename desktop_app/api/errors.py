from dataclasses import dataclass

import requests


@dataclass
class ApiError(Exception):
    user_message: str
    technical_message: str = ""
    status_code: int | None = None

    def __str__(self) -> str:
        return self.user_message


def map_exception_to_user_message(exc: Exception) -> str:
    if isinstance(exc, requests.Timeout):
        return "Истекло время ожидания ответа от сервера."
    if isinstance(exc, requests.ConnectionError):
        return "Не удалось подключиться к серверу. Проверьте, запущен ли backend."
    if isinstance(exc, requests.HTTPError):
        return "Сервер вернул ошибку при обработке запроса."
    if isinstance(exc, requests.RequestException):
        return "Сервер временно недоступен."
    return "Произошла ошибка при обращении к серверу."

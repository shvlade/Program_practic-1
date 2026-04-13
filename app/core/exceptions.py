"""
Кастомные исключения для приложения
"""


class BaseAppError(Exception):
    """Базовое исключение для всего приложения"""
    pass


class FatalError(BaseAppError):
    """Критические ошибки, требующие остановки программы"""
    pass


class DataFormatError(BaseAppError):
    """Ошибка структуры файла (неправильный формат, поврежденные данные)"""
    pass


class ValidationError(BaseAppError):
    """Ошибка бизнес-логики (невалидные данные записи)"""
    pass


class CurrencyMismatchError(ValidationError):
    """Ошибка: разные валюты в одном отчете"""
    pass


class DuplicateIdError(ValidationError):
    """Ошибка: дубликат ID транзакции"""
    pass

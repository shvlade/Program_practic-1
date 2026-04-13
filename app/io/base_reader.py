"""
Абстрактный базовый класс для всех читателей файлов
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
import logging

from app.core.models import Transaction
from app.core.exceptions import DataFormatError

logger = logging.getLogger(__name__)


class BaseReader(ABC):
    """Абстрактный класс для чтения файлов"""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self._transactions: List[Transaction] = []

    @abstractmethod
    def read(self) -> List[Transaction]:
        """
        Прочитать файл и вернуть список транзакций
        Должен выбрасывать DataFormatError при ошибках формата
        """
        pass

    def _validate_file_exists(self) -> None:
        """Проверить существование файла"""
        if not self.file_path.exists():
            raise DataFormatError(
                f"Файл не существует: {self.file_path}"
            )

        if not self.file_path.is_file():
            raise DataFormatError(
                f"Путь не является файлом: {self.file_path}"
            )

    def _validate_file_size(self, max_size_mb: int = 100) -> None:
        """Проверить размер файла"""
        try:
            size_mb = self.file_path.stat().st_size / (1024 * 1024)
            if size_mb > max_size_mb:
                raise DataFormatError(
                    f"Файл слишком большой: {size_mb:.2f} MB "
                    f"(макс {max_size_mb} MB)"
                )
        except OSError as e:
            raise DataFormatError(f"Ошибка доступа к файлу: {e}")

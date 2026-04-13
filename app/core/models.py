"""
Модели данных с использованием dataclasses
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict


@dataclass
class Transaction:
    """Модель финансовой транзакции"""
    id: str
    amount: Decimal
    category: str
    date: datetime
    currency: str = "RUB"
    source_file: Optional[str] = None

    def __post_init__(self):
        """Дополнительная валидация после инициализации"""
        if isinstance(self.amount, (int, float)):
            self.amount = Decimal(str(self.amount))
        if isinstance(self.date, str):
            self.date = datetime.fromisoformat(
                self.date.replace('Z', '+00:00')
            )

    def to_dict(self) -> dict:
        """Конвертация в словарь для JSON"""
        return {
            'id': self.id,
            'amount': float(self.amount),
            'category': self.category,
            'date': self.date.isoformat(),
            'currency': self.currency,
            'source_file': self.source_file
        }


@dataclass
class ProcessingError:
    """Модель ошибки обработки"""
    file_name: str
    line_number: Optional[int]
    error_type: str
    error_message: str
    raw_data: Optional[dict] = None


@dataclass
class ProcessingResult:
    """Результат обработки"""
    total_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    total_transactions: int = 0
    valid_transactions: int = 0
    errors: List[ProcessingError] = field(default_factory=list)
    aggregated_data: Dict[str, float] = field(default_factory=dict)

    def add_error(self, error: ProcessingError):
        """Добавить ошибку"""
        self.errors.append(error)
        self.failed_files += 1

    def add_success(self, transactions_count: int):
        """Добавить успешный файл"""
        self.successful_files += 1
        self.total_transactions += transactions_count
        self.valid_transactions += transactions_count
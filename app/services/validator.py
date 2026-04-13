"""
Сервис валидации транзакций
"""

from decimal import Decimal
from typing import List, Set
import logging

from app.core.models import Transaction
from app.core.exceptions import (
    ValidationError,
    CurrencyMismatchError,
    DuplicateIdError
)

logger = logging.getLogger(__name__)


class TransactionValidator:
    """Валидатор транзакций"""

    def __init__(self):
        self.processed_ids: Set[str] = set()

    def validate(self, transaction: Transaction) -> bool:
        """
        Валидация транзакции
        Возвращает True если валидна, иначе выбрасывает исключение
        """
        if not transaction.id or not transaction.id.strip():
            raise ValidationError("ID транзакции не может быть пустым")

        if transaction.id in self.processed_ids:
            raise DuplicateIdError(
                f"Дубликат ID транзакции: {transaction.id}"
            )

        if transaction.amount <= 0:
            raise ValidationError(
                f"Сумма транзакции должна быть положительной, "
                f"получено: {transaction.amount}"
            )

        if transaction.amount > Decimal('1000000000'):
            raise ValidationError(
                f"Сумма транзакции превышает лимит: {transaction.amount}"
            )

        if not transaction.category or not transaction.category.strip():
            raise ValidationError(
                "Категория транзакции не может быть пустой"
            )

        if len(transaction.category) > 100:
            raise ValidationError(
                f"Название категории слишком длинное: "
                f"{len(transaction.category)} символов"
            )

        allowed_currencies = {'RUB', 'USD', 'EUR', 'GBP', 'CNY'}
        if transaction.currency not in allowed_currencies:
            raise ValidationError(
                f"Неподдерживаемая валюта: {transaction.currency}. "
                f"Допустимые: {allowed_currencies}"
            )

        self.processed_ids.add(transaction.id)
        return True

    def validate_currency_consistency(
        self,
        transactions: List[Transaction]
    ) -> None:
        """
        Проверка консистентности валют в наборе транзакций
        """
        if not transactions:
            return

        currencies = {t.currency for t in transactions}
        if len(currencies) > 1:
            raise CurrencyMismatchError(
                f"Обнаружены разные валюты в одном отчете: {currencies}"
            )

    def reset(self):
        """Сброс состояния валидатора"""
        self.processed_ids.clear()

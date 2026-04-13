"""
Сервис агрегации данных
"""

from typing import Dict, List
from decimal import Decimal
import logging

from app.core.models import Transaction

logger = logging.getLogger(__name__)


class DataAggregator:
    """Агрегатор транзакций по категориям"""

    def __init__(self):
        self.category_sums: Dict[str, Decimal] = {}
        self.all_transactions: List[Transaction] = []

    def add_transactions(self, transactions: List[Transaction]) -> None:
        """Добавить транзакции для агрегации"""
        for transaction in transactions:
            self.all_transactions.append(transaction)

            if transaction.category not in self.category_sums:
                self.category_sums[transaction.category] = Decimal('0')

            self.category_sums[transaction.category] += transaction.amount

    def get_aggregated_data(self) -> Dict[str, float]:
        """Получить агрегированные данные"""
        return {
            category: float(amount)
            for category, amount in self.category_sums.items()
        }

    def get_all_transactions(self) -> List[Transaction]:
        """Получить все транзакции"""
        return self.all_transactions

    def reset(self):
        """Сброс агрегатора"""
        self.category_sums.clear()
        self.all_transactions.clear()

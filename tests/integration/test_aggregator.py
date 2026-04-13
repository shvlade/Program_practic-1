"""
Интеграционные тесты для агрегатора
"""

import pytest
from decimal import Decimal
from datetime import datetime

from app.services.aggregator import DataAggregator
from app.core.models import Transaction


class TestDataAggregator:
    """Тесты для DataAggregator"""

    def test_add_single_transaction(self):
        """Добавление одной транзакции"""
        aggregator = DataAggregator()
        transaction = Transaction(
            id="TRX001",
            amount=Decimal("100.50"),
            category="Продукты",
            date=datetime(2024, 1, 1)
        )

        aggregator.add_transactions([transaction])

        result = aggregator.get_aggregated_data()
        assert result["Продукты"] == 100.50
        assert len(aggregator.get_all_transactions()) == 1

    def test_aggregate_multiple_transactions_same_category(self):
        """Агрегация нескольких транзакций одной категории"""
        aggregator = DataAggregator()
        transactions = [
            Transaction(id="1", amount=Decimal("100"), category="Продукты", date=datetime.now()),
            Transaction(id="2", amount=Decimal("200"), category="Продукты", date=datetime.now()),
            Transaction(id="3", amount=Decimal("300"), category="Продукты", date=datetime.now()),
        ]

        aggregator.add_transactions(transactions)

        result = aggregator.get_aggregated_data()
        assert result["Продукты"] == 600.00

    def test_aggregate_multiple_categories(self):
        """Агрегация транзакций разных категорий"""
        aggregator = DataAggregator()
        transactions = [
            Transaction(id="1", amount=Decimal("100"), category="Продукты", date=datetime.now()),
            Transaction(id="2", amount=Decimal("200"), category="Транспорт", date=datetime.now()),
            Transaction(id="3", amount=Decimal("300"), category="Рестораны", date=datetime.now()),
        ]

        aggregator.add_transactions(transactions)

        result = aggregator.get_aggregated_data()
        assert result["Продукты"] == 100.00
        assert result["Транспорт"] == 200.00
        assert result["Рестораны"] == 300.00

    def test_reset_aggregator(self):
        """Сброс агрегатора"""
        aggregator = DataAggregator()
        transaction = Transaction(
            id="TRX001",
            amount=Decimal("100"),
            category="Тест",
            date=datetime.now()
        )

        aggregator.add_transactions([transaction])
        assert len(aggregator.get_all_transactions()) == 1

        aggregator.reset()
        assert len(aggregator.get_all_transactions()) == 0
        assert aggregator.get_aggregated_data() == {}
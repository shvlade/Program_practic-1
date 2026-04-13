"""
Unit-тесты для моделей данных
"""

import pytest
from decimal import Decimal
from datetime import datetime

from app.core.models import Transaction, ProcessingError, ProcessingResult


class TestTransaction:
    """Тесты для модели Transaction"""

    def test_create_valid_transaction(self):
        """Создание валидной транзакции"""
        transaction = Transaction(
            id="TEST001",
            amount=Decimal("100.50"),
            category="Тест",
            date=datetime(2024, 1, 1),
            currency="RUB"
        )

        assert transaction.id == "TEST001"
        assert transaction.amount == Decimal("100.50")
        assert transaction.category == "Тест"
        assert transaction.date == datetime(2024, 1, 1)
        assert transaction.currency == "RUB"

    def test_transaction_with_float_amount(self):
        """Создание транзакции с float суммой"""
        transaction = Transaction(
            id="TEST002",
            amount=100.50,
            category="Тест",
            date=datetime(2024, 1, 1)
        )

        assert isinstance(transaction.amount, Decimal)
        assert transaction.amount == Decimal("100.50")

    def test_transaction_with_string_date(self):
        """Создание транзакции со строковой датой"""
        transaction = Transaction(
            id="TEST003",
            amount=Decimal("50.00"),
            category="Тест",
            date="2024-01-01"
        )

        assert isinstance(transaction.date, datetime)
        assert transaction.date == datetime(2024, 1, 1)

    def test_to_dict_conversion(self):
        """Конвертация транзакции в словарь"""
        transaction = Transaction(
            id="TEST004",
            amount=Decimal("75.25"),
            category="Конвертация",
            date=datetime(2024, 1, 1),
            currency="USD",
            source_file="test.csv"
        )

        result = transaction.to_dict()

        assert result['id'] == "TEST004"
        assert result['amount'] == 75.25
        assert result['category'] == "Конвертация"
        assert result['date'] == "2024-01-01T00:00:00"
        assert result['currency'] == "USD"
        assert result['source_file'] == "test.csv"


class TestProcessingResult:
    """Тесты для ProcessingResult"""

    def test_add_error(self):
        """Добавление ошибки в результат"""
        result = ProcessingResult()
        error = ProcessingError(
            file_name="test.csv",
            line_number=5,
            error_type="ValidationError",
            error_message="Invalid amount"
        )

        result.add_error(error)

        assert len(result.errors) == 1
        assert result.failed_files == 1

    def test_add_success(self):
        """Добавление успешной обработки"""
        result = ProcessingResult()

        result.add_success(10)

        assert result.successful_files == 1
        assert result.total_transactions == 10
        assert result.valid_transactions == 10

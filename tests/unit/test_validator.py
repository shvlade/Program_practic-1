"""
Unit-тесты для валидатора с параметризацией
"""

import pytest
from decimal import Decimal
from datetime import datetime

from app.services.validator import TransactionValidator
from app.core.models import Transaction
from app.core.exceptions import (
    ValidationError,
    CurrencyMismatchError,
    DuplicateIdError
)


class TestTransactionValidator:
    """Тесты для TransactionValidator"""

    def setup_method(self):
        """Подготовка перед каждым тестом"""
        self.validator = TransactionValidator()

    @pytest.mark.parametrize("amount, expected_valid", [
        (Decimal("0.01"), True),      # Минимальная сумма - ВАЛИДНО
        (Decimal("0.001"), True),     # Очень маленькая сумма
        (Decimal("100.50"), True),    # Обычная сумма
        (Decimal("1000000"), True),   # Большая сумма
        (Decimal("999999999"), True), # Почти лимит
        (Decimal("0"), False),        # Ноль - НЕВАЛИДНО
        (Decimal("-0.01"), False),    # Отрицательная сумма
        (Decimal("-100"), False),     # Отрицательная сумма
        (Decimal("1000000001"), False), # Превышение лимита
        (Decimal("-0.001"), False),   # Отрицательная маленькая
    ])
    def test_validate_amount(self, amount, expected_valid):
        """Проверка валидации суммы (граничные значения)"""
        transaction = Transaction(
            id="TEST001",
            amount=amount,
            category="Тест",
            date=datetime(2024, 1, 1)
        )

        if expected_valid:
            assert self.validator.validate(transaction) is True
        else:
            with pytest.raises(ValidationError):
                self.validator.validate(transaction)

    @pytest.mark.parametrize("currency, expected_valid", [
        ("RUB", True),
        ("USD", True),
        ("EUR", True),
        ("GBP", True),
        ("CNY", True),
        ("JPY", False),
        ("XXX", False),
        ("", False),
        ("   ", False),
        ("usd", False),  # должен быть uppercase
    ])
    def test_validate_currency(self, currency, expected_valid):
        """Проверка валидации валюты"""
        transaction = Transaction(
            id="TEST001",
            amount=Decimal("100"),
            category="Тест",
            date=datetime(2024, 1, 1),
            currency=currency
        )

        if expected_valid:
            assert self.validator.validate(transaction) is True
        else:
            with pytest.raises(ValidationError):
                self.validator.validate(transaction)

    @pytest.mark.parametrize("category, expected_valid", [
        ("Продукты", True),
        ("Транспорт", True),
        ("Очень длинная категория" * 10, False),
        ("", False),
        ("   ", False),
        ("A" * 100, True),   # ровно 100 символов
        ("A" * 101, False),  # 101 символ
        ("Книги и журналы", True),
    ])
    def test_validate_category(self, category, expected_valid):
        """Проверка валидации категории"""
        transaction = Transaction(
            id="TEST001",
            amount=Decimal("100"),
            category=category,
            date=datetime(2024, 1, 1)
        )

        if expected_valid:
            assert self.validator.validate(transaction) is True
        else:
            with pytest.raises(ValidationError):
                self.validator.validate(transaction)

    @pytest.mark.parametrize("id_value, expected_valid", [
        ("VALID_ID", True),
        ("123", True),
        ("TRX-001-ABC", True),
        ("", False),
        ("   ", False),
        (None, False),
    ])
    def test_validate_id(self, id_value, expected_valid):
        """Проверка валидации ID"""
        if id_value is None:
            id_value = ""

        transaction = Transaction(
            id=id_value,
            amount=Decimal("100"),
            category="Тест",
            date=datetime(2024, 1, 1)
        )

        if expected_valid:
            assert self.validator.validate(transaction) is True
        else:
            with pytest.raises(ValidationError):
                self.validator.validate(transaction)

    def test_duplicate_id_detection(self):
        """Проверка обнаружения дубликатов ID"""
        transaction1 = Transaction(
            id="DUPLICATE",
            amount=Decimal("100"),
            category="Тест",
            date=datetime(2024, 1, 1)
        )
        transaction2 = Transaction(
            id="DUPLICATE",
            amount=Decimal("200"),
            category="Тест",
            date=datetime(2024, 1, 2)
        )

        assert self.validator.validate(transaction1) is True

        with pytest.raises(DuplicateIdError, match="Дубликат ID"):
            self.validator.validate(transaction2)

    def test_validate_currency_consistency_same_currency(self):
        """Проверка консистентности валют - все одинаковые"""
        transactions = [
            Transaction(id="1", amount=Decimal("100"), category="A", date=datetime.now(), currency="RUB"),
            Transaction(id="2", amount=Decimal("200"), category="B", date=datetime.now(), currency="RUB"),
            Transaction(id="3", amount=Decimal("300"), category="C", date=datetime.now(), currency="RUB"),
        ]

        self.validator.validate_currency_consistency(transactions)

    def test_validate_currency_consistency_different_currencies(self):
        """Проверка консистентности валют - разные валюты"""
        transactions = [
            Transaction(id="1", amount=Decimal("100"), category="A", date=datetime.now(), currency="RUB"),
            Transaction(id="2", amount=Decimal("200"), category="B", date=datetime.now(), currency="USD"),
            Transaction(id="3", amount=Decimal("300"), category="C", date=datetime.now(), currency="EUR"),
        ]

        with pytest.raises(CurrencyMismatchError, match="разные валюты"):
            self.validator.validate_currency_consistency(transactions)

    def test_empty_transactions_list(self):
        """Проверка пустого списка транзакций"""
        self.validator.validate_currency_consistency([])

    def test_reset_validator(self):
        """Проверка сброса валидатора"""
        transaction = Transaction(
            id="RESET001",
            amount=Decimal("100"),
            category="Тест",
            date=datetime(2024, 1, 1)
        )

        self.validator.validate(transaction)

        with pytest.raises(DuplicateIdError):
            self.validator.validate(transaction)

        self.validator.reset()

        assert self.validator.validate(transaction) is True
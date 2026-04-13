"""
Unit-тесты для кастомных исключений
"""

import pytest

from app.core.exceptions import (
    BaseAppError,
    FatalError,
    DataFormatError,
    ValidationError,
    CurrencyMismatchError,
    DuplicateIdError
)


class TestExceptions:
    """Тесты для иерархии исключений"""

    def test_exception_hierarchy(self):
        """Проверка иерархии исключений"""
        assert issubclass(FatalError, BaseAppError)
        assert issubclass(DataFormatError, BaseAppError)
        assert issubclass(ValidationError, BaseAppError)
        assert issubclass(CurrencyMismatchError, ValidationError)
        assert issubclass(DuplicateIdError, ValidationError)

    def test_fatal_error_creation(self):
        """Создание FatalError"""
        error = FatalError("Critical error occurred")
        assert str(error) == "Critical error occurred"
        assert isinstance(error, BaseAppError)

    def test_data_format_error_creation(self):
        """Создание DataFormatError"""
        error = DataFormatError("Invalid CSV format")
        assert str(error) == "Invalid CSV format"
        assert isinstance(error, BaseAppError)

    def test_validation_error_creation(self):
        """Создание ValidationError"""
        error = ValidationError("Amount must be positive")
        assert str(error) == "Amount must be positive"
        assert isinstance(error, BaseAppError)

    def test_currency_mismatch_error_creation(self):
        """Создание CurrencyMismatchError"""
        error = CurrencyMismatchError("Different currencies found")
        assert str(error) == "Different currencies found"
        assert isinstance(error, ValidationError)

    def test_duplicate_id_error_creation(self):
        """Создание DuplicateIdError"""
        error = DuplicateIdError("Duplicate ID: TRX001")
        assert str(error) == "Duplicate ID: TRX001"
        assert isinstance(error, ValidationError)
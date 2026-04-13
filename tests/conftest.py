"""
Общие фикстуры для всех тестов
"""
"""
Общие фикстуры для всех тестов
"""

import pytest
import json
from pathlib import Path
from decimal import Decimal
from datetime import datetime

from app.core.models import Transaction, ProcessingResult, ProcessingError


@pytest.fixture
def sample_transaction():
    """Создает валидную транзакцию для тестов"""
    return Transaction(
        id="TEST001",
        amount=Decimal("100.50"),
        category="Тест",
        date=datetime(2024, 1, 1),
        currency="RUB",
        source_file="test.csv"
    )


@pytest.fixture
def sample_transactions():
    """Создает список валидных транзакций"""
    return [
        Transaction(
            id="TRX001",
            amount=Decimal("1000.00"),
            category="Продукты",
            date=datetime(2024, 1, 1),
            currency="RUB"
        ),
        Transaction(
            id="TRX002",
            amount=Decimal("2500.00"),
            category="Транспорт",
            date=datetime(2024, 1, 2),
            currency="RUB"
        ),
        Transaction(
            id="TRX003",
            amount=Decimal("4200.00"),
            category="Рестораны",
            date=datetime(2024, 1, 3),
            currency="RUB"
        )
    ]


@pytest.fixture
def temp_csv_file(tmp_path):
    """Создает временный CSV файл"""

    def _create_csv(content: str, filename: str = "test.csv"):
        file_path = tmp_path / filename
        file_path.write_text(content, encoding='utf-8')
        return file_path

    return _create_csv


@pytest.fixture
def temp_json_file(tmp_path):
    """Создает временный JSON файл"""

    def _create_json(data, filename: str = "test.json"):
        file_path = tmp_path / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return file_path

    return _create_json


@pytest.fixture
def clean_processor():
    """Создает чистый процессор для тестов"""
    from app.services.processor import DataProcessor
    from app.services.validator import TransactionValidator
    from app.services.aggregator import DataAggregator

    processor = DataProcessor(Path("dummy"), Path("dummy.json"))
    processor.validator = TransactionValidator()
    processor.aggregator = DataAggregator()
    processor.result = ProcessingResult()
    return processor

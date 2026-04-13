"""
Интеграционные тесты для JSON Reader с использованием tmp_path
"""

import pytest
import json
from decimal import Decimal

from app.io.json_reader import JSONReader
from app.core.exceptions import DataFormatError


class TestJSONReader:
    """Тесты для JSONReader с использованием tmp_path"""

    def test_read_valid_json_list(self, tmp_path):
        """Чтение валидного JSON (список)"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.json"

        json_data = [
            {"id": "TRX001", "amount": 100.50, "category": "Продукты", "date": "2024-01-01", "currency": "RUB"},
            {"id": "TRX002", "amount": 250.00, "category": "Транспорт", "date": "2024-01-02", "currency": "USD"}
        ]

        with open(p, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        reader = JSONReader(p)
        transactions = reader.read()

        assert len(transactions) == 2
        assert transactions[0].id == "TRX001"
        assert transactions[0].amount == Decimal("100.50")

    def test_read_valid_json_object(self, tmp_path):
        """Чтение валидного JSON (объект с ключом transactions)"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.json"

        json_data = {
            "transactions": [
                {"id": "TRX001", "amount": 100.50, "category": "Продукты", "date": "2024-01-01", "currency": "RUB"},
                {"id": "TRX002", "amount": 250.00, "category": "Транспорт", "date": "2024-01-02", "currency": "USD"}
            ]
        }

        with open(p, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        reader = JSONReader(p)
        transactions = reader.read()

        assert len(transactions) == 2

    def test_read_json_with_one_good_and_two_bad_items(self, tmp_path):
        """Тест: 1 хорошая и 2 плохие записи"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.json"

        json_data = [
            {"id": "GOOD001", "amount": 100.50, "category": "Продукты", "date": "2024-01-01", "currency": "RUB"},
            {"id": "BAD001", "amount": "invalid", "category": "Ошибка", "date": "2024-01-02", "currency": "RUB"},
            {"id": "BAD002", "amount": -100, "category": "Отрицательная", "date": "2024-01-03", "currency": "RUB"},
        ]

        with open(p, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        reader = JSONReader(p)
        transactions = reader.read()

        # Проверяем, что GOOD001 прочитан
        good_ids = [t.id for t in transactions]
        assert "GOOD001" in good_ids

        # Проверяем, что количество прочитанных транзакций >= 1
        assert len(transactions) >= 1

    def test_read_json_missing_fields(self, tmp_path):
        """Чтение JSON с пропущенными полями"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.json"

        json_data = [
            {"id": "TRX001", "amount": 100.50}  # missing category and date
        ]

        with open(p, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        reader = JSONReader(p)
        transactions = reader.read()

        assert len(transactions) == 0
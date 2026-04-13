"""
Интеграционные тесты для CSV Reader с использованием tmp_path
"""

import pytest
from decimal import Decimal
from datetime import datetime

from app.io.csv_reader import CSVReader
from app.core.exceptions import DataFormatError


class TestCSVReader:
    """Тесты для CSVReader с использованием tmp_path"""

    def test_read_valid_csv(self, tmp_path):
        """Чтение валидного CSV файла"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.csv"

        csv_content = """id,amount,category,date,currency
TRX001,100.50,Продукты,2024-01-01,RUB
TRX002,250.00,Транспорт,2024-01-02,USD
TRX003,420.75,Рестораны,2024-01-03,EUR
"""
        p.write_text(csv_content, encoding='utf-8')

        reader = CSVReader(p)
        transactions = reader.read()

        assert len(transactions) == 3
        assert transactions[0].id == "TRX001"
        assert transactions[0].amount == Decimal("100.50")

    def test_read_csv_with_semicolon(self, tmp_path):
        """Чтение CSV с разделителем точка с запятой"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.csv"

        csv_content = """id;amount;category;date;currency
TRX001;100.50;Продукты;2024-01-01;RUB
TRX002;250.00;Транспорт;2024-01-02;USD
"""
        p.write_text(csv_content, encoding='utf-8')

        reader = CSVReader(p)
        transactions = reader.read()

        assert len(transactions) == 2

    def test_read_csv_with_one_good_and_two_bad_rows(self, tmp_path):
        """Тест: 1 хорошая и 2 плохие строки"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.csv"

        csv_content = """id,amount,category,date,currency
GOOD001,100.50,Продукты,2024-01-01,RUB
BAD001,invalid,Ошибка,2024-01-02,RUB
BAD002,-100,Отрицательная,2024-01-03,RUB
"""
        p.write_text(csv_content, encoding='utf-8')

        reader = CSVReader(p)
        transactions = reader.read()

        # Проверяем, что GOOD001 прочитан
        good_ids = [t.id for t in transactions]
        assert "GOOD001" in good_ids

        # Проверяем, что количество прочитанных транзакций >= 1
        assert len(transactions) >= 1

    def test_read_csv_missing_headers(self, tmp_path):
        """Чтение CSV без заголовков"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.csv"

        csv_content = """TRX001,100.50,Продукты,2024-01-01,RUB
TRX002,250.00,Транспорт,2024-01-02,USD
"""
        p.write_text(csv_content, encoding='utf-8')

        reader = CSVReader(p)

        # Проверяем, что выбрасывается исключение DataFormatError
        with pytest.raises(DataFormatError):
            reader.read()

    def test_read_empty_csv(self, tmp_path):
        """Чтение пустого CSV файла"""
        d = tmp_path / "data"
        d.mkdir()
        p = d / "test.csv"

        csv_content = """id,amount,category,date,currency
"""
        p.write_text(csv_content, encoding='utf-8')

        reader = CSVReader(p)
        transactions = reader.read()

        assert len(transactions) == 0

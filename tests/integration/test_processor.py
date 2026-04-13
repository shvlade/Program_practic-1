"""
Интеграционные тесты для процессора
"""

import pytest
import json
from pathlib import Path
from unittest.mock import patch

from app.services.processor import DataProcessor
from app.core.exceptions import FatalError


class TestDataProcessor:
    """Тесты для DataProcessor"""

    def test_processor_nonexistent_directory(self):
        """Тест с несуществующей директорией"""
        processor = DataProcessor(Path("/nonexistent/directory"))

        with pytest.raises(FatalError, match="Директория не существует"):
            processor.process_all()

    def test_processor_with_valid_csv(self, tmp_path):
        """Тест процессора с валидным CSV"""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        csv_content = """id,amount,category,date,currency
TRX001,100.50,Продукты,2024-01-01,RUB
TRX002,250.00,Транспорт,2024-01-02,RUB
"""
        p = data_dir / "test.csv"
        p.write_text(csv_content, encoding='utf-8')

        output_file = tmp_path / "result.json"
        processor = DataProcessor(data_dir, output_file)

        result = processor.process_all()

        assert result.total_files == 1
        assert result.valid_transactions == 2

    def test_processor_with_one_good_and_two_bad_rows(self, tmp_path):
        """Тест: 1 хорошая и 2 плохие строки"""
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        csv_content = """id,amount,category,date,currency
GOOD001,100.50,Продукты,2024-01-01,RUB
BAD001,invalid,Ошибка,2024-01-02,RUB
BAD002,-100,Отрицательная,2024-01-03,RUB
"""
        p = data_dir / "test.csv"
        p.write_text(csv_content, encoding='utf-8')

        output_file = tmp_path / "result.json"
        processor = DataProcessor(data_dir, output_file)

        result = processor.process_all()

        assert result.valid_transactions == 1

        assert output_file.exists()
        with open(output_file, 'r', encoding='utf-8') as f:
            output_data = json.load(f)

        assert len(output_data['all_valid_transactions']) == 1
        assert output_data['all_valid_transactions'][0]['id'] == "GOOD001"

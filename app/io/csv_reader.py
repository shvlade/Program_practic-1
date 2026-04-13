"""
Читатель CSV файлов
"""

import csv
from pathlib import Path
from typing import List
from datetime import datetime
from decimal import Decimal
import logging

from app.io.base_reader import BaseReader
from app.core.models import Transaction
from app.core.exceptions import DataFormatError

logger = logging.getLogger(__name__)


class CSVReader(BaseReader):
    """Чтение CSV файлов с транзакциями"""

    def __init__(self, file_path: Path, encoding: str = 'utf-8'):
        super().__init__(file_path)
        self.encoding = encoding

    def read(self) -> List[Transaction]:
        """Прочитать CSV файл"""
        self._validate_file_exists()
        self._validate_file_size()

        transactions: List[Transaction] = []

        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                first_lines = []
                for _ in range(5):
                    line = file.readline()
                    if not line:
                        break
                    first_lines.append(line)
                file.seek(0)

                delimiters = [',', ';', '\t', '|']
                detected_delimiter = None

                for delimiter in delimiters:
                    try:
                        sample = ''.join(first_lines[:2])
                        if delimiter in sample:
                            test_reader = csv.reader(first_lines, delimiter=delimiter)
                            rows = list(test_reader)
                            if rows and len(rows[0]) > 1:
                                field_counts = [len(row) for row in rows]
                                if len(set(field_counts)) == 1:
                                    detected_delimiter = delimiter
                                    break
                    except Exception:
                        continue

                if not detected_delimiter:
                    detected_delimiter = ','

                csv_reader = csv.DictReader(file, delimiter=detected_delimiter)

                required_fields = {'id', 'amount', 'category', 'date'}
                if csv_reader.fieldnames:
                    fieldnames_lower = [f.lower() for f in csv_reader.fieldnames]
                    if not required_fields.issubset(set(fieldnames_lower)):
                        missing = required_fields - set(fieldnames_lower)
                        raise DataFormatError(
                            f"Отсутствуют обязательные поля: {missing}. "
                            f"Найдены: {csv_reader.fieldnames}"
                        )
                else:
                    raise DataFormatError("CSV файл не содержит заголовков")

                for row_num, row in enumerate(csv_reader, start=2):
                    try:
                        normalized_row = {k.lower(): v for k, v in row.items()}
                        transaction = self._parse_row(normalized_row, row_num)
                        transactions.append(transaction)
                    except (ValueError, KeyError) as e:
                        logger.error(
                            f"Ошибка парсинга строки {row_num} в файле "
                            f"{self.file_path.name}: {e}"
                        )
                        continue

                logger.debug(
                    f"Прочитано {len(transactions)} транзакций из "
                    f"{self.file_path.name}"
                )
                return transactions

        except csv.Error as e:
            raise DataFormatError(f"Ошибка парсинга CSV: {e}")
        except UnicodeDecodeError as e:
            raise DataFormatError(f"Ошибка кодировки файла: {e}")
        except PermissionError as e:
            raise DataFormatError(f"Нет доступа к файлу: {e}")
        except Exception as e:
            raise DataFormatError(f"Неожиданная ошибка при чтении файла: {e}")

    def _parse_row(self, row: dict, line_num: int) -> Transaction:
        """Парсинг одной строки CSV"""
        try:
            amount_str = (
                str(row['amount'])
                .strip()
                .replace(',', '.')
                .replace(' ', '')
            )
            if not amount_str:
                raise ValueError("Пустое значение amount")
            amount = Decimal(amount_str)

            date_str = str(row['date']).strip()
            if not date_str:
                raise ValueError("Пустое значение date")
            date = self._parse_date(date_str)

            return Transaction(
                id=str(row['id']).strip(),
                amount=amount,
                category=str(row['category']).strip(),
                date=date,
                currency=str(row.get('currency', 'RUB')).strip(),
                source_file=str(self.file_path)
            )
        except Exception as e:
            raise ValueError(
                f"Ошибка парсинга строки {line_num}: {e}, данные: {row}"
            )

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Парсинг даты в разных форматах"""
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%Y%m%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Не удалось распарсить дату: {date_str}")
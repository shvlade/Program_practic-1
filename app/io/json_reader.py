"""
Читатель JSON файлов
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from decimal import Decimal
import logging

from app.io.base_reader import BaseReader
from app.core.models import Transaction
from app.core.exceptions import DataFormatError

logger = logging.getLogger(__name__)


class JSONReader(BaseReader):
    """Чтение JSON файлов с транзакциями"""

    def __init__(self, file_path: Path, encoding: str = 'utf-8'):
        super().__init__(file_path)
        self.encoding = encoding

    def read(self) -> List[Transaction]:
        """Прочитать JSON файл"""
        self._validate_file_exists()
        self._validate_file_size()

        transactions = []

        try:
            with open(self.file_path, 'r', encoding=self.encoding) as file:
                data = json.load(file)

            if isinstance(data, list):
                transactions_list = data
            elif isinstance(data, dict) and 'transactions' in data:
                transactions_list = data['transactions']
            else:
                raise DataFormatError(
                    "JSON должен быть списком транзакций или объектом "
                    "с ключом 'transactions'"
                )

            if not isinstance(transactions_list, list):
                raise DataFormatError(
                    "Поле 'transactions' должно быть списком"
                )

            for idx, item in enumerate(transactions_list):
                try:
                    transaction = self._parse_item(item, idx + 1)
                    transactions.append(transaction)
                except (ValueError, KeyError) as e:
                    logger.error(
                        f"Ошибка парсинга элемента {idx + 1} в файле "
                        f"{self.file_path.name}: {e}"
                    )
                    continue

            logger.debug(
                f"Прочитано {len(transactions)} транзакций из "
                f"{self.file_path.name}"
            )
            return transactions

        except json.JSONDecodeError as e:
            raise DataFormatError(f"Ошибка парсинга JSON: {e}")
        except UnicodeDecodeError as e:
            raise DataFormatError(f"Ошибка кодировки файла: {e}")
        except PermissionError as e:
            raise DataFormatError(f"Нет доступа к файлу: {e}")
        except Exception as e:
            raise DataFormatError(f"Неожиданная ошибка при чтении файла: {e}")

    def _parse_item(self, item: Dict[str, Any], idx: int) -> Transaction:
        """Парсинг одного JSON объекта"""
        if not isinstance(item, dict):
            raise ValueError(f"Элемент {idx} не является объектом")

        required_fields = {'id', 'amount', 'category', 'date'}

        if not required_fields.issubset(set(item.keys())):
            missing = required_fields - set(item.keys())
            raise KeyError(f"Отсутствуют обязательные поля: {missing}")

        try:
            amount_value = item['amount']
            if isinstance(amount_value, (int, float)):
                amount = Decimal(str(amount_value))
            elif isinstance(amount_value, str):
                cleaned = (
                    amount_value.strip()
                    .replace(',', '.')
                    .replace(' ', '')
                )
                if not cleaned:
                    raise ValueError("Пустое значение amount")
                amount = Decimal(cleaned)
            else:
                raise ValueError(
                    f"Некорректный тип amount: {type(amount_value)}"
                )

            date_value = item['date']
            if isinstance(date_value, str):
                date = self._parse_date(date_value)
            elif isinstance(date_value, (int, float)):
                date = datetime.fromtimestamp(date_value)
            elif isinstance(date_value, dict) and '$date' in date_value:
                date = self._parse_date(str(date_value['$date']))
            else:
                raise ValueError(
                    f"Некорректный формат даты: {date_value}"
                )

            return Transaction(
                id=str(item['id']),
                amount=amount,
                category=str(item['category']),
                date=date,
                currency=str(item.get('currency', 'RUB')),
                source_file=str(self.file_path)
            )
        except Exception as e:
            raise ValueError(f"Ошибка парсинга элемента {idx}: {e}")

    @staticmethod
    def _parse_date(date_str: str) -> datetime:
        """Парсинг даты в разных форматах"""
        formats = [
            '%Y-%m-%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%fZ',
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%Y%m%d'
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        raise ValueError(f"Не удалось распарсить дату: {date_str}")

"""
Пакет для работы с вводом/выводом
"""

from app.io.base_reader import BaseReader
from app.io.csv_reader import CSVReader
from app.io.json_reader import JSONReader

READER_REGISTRY = {
    '.csv': CSVReader,
    '.json': JSONReader,
}

__all__ = ['BaseReader', 'CSVReader', 'JSONReader', 'READER_REGISTRY']

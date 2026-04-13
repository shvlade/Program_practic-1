"""
Основной оркестратор обработки данных
"""

from pathlib import Path
from typing import List
import logging
import json
import shutil

from app.core.models import ProcessingResult, ProcessingError
from app.core.exceptions import (
    DataFormatError,
    ValidationError,
    CurrencyMismatchError,
    DuplicateIdError,
    FatalError
)
from app.io import READER_REGISTRY
from app.services.validator import TransactionValidator
from app.services.aggregator import DataAggregator

logger = logging.getLogger(__name__)


class DataProcessor:
    """Основной процессор данных"""

    def __init__(
        self,
        data_dir: Path,
        output_file: Path = Path('result.json')
    ):
        self.data_dir = Path(data_dir)
        self.output_file = Path(output_file)
        self.validator = TransactionValidator()
        self.aggregator = DataAggregator()
        self.result = ProcessingResult()

    def process_all(self) -> ProcessingResult:
        """Обработать все файлы в директории"""
        if not self.data_dir.exists():
            raise FatalError(f"Директория не существует: {self.data_dir}")

        if not self.data_dir.is_dir():
            raise FatalError(f"Путь не является директорией: {self.data_dir}")

        files_to_process = self._get_files_to_process()
        self.result.total_files = len(files_to_process)

        for file_path in files_to_process:
            self._process_single_file(file_path)

        self.result.aggregated_data = self.aggregator.get_aggregated_data()
        self._save_result()

        return self.result

    def _get_files_to_process(self) -> List[Path]:
        """Получить список файлов для обработки"""
        files: List[Path] = []

        for ext in READER_REGISTRY.keys():
            files.extend(self.data_dir.glob(f"*{ext}"))
            files.extend(self.data_dir.glob(f"*{ext.upper()}"))

        unique_files = list(set(files))
        return sorted(unique_files)

    def _process_single_file(self, file_path: Path) -> None:
        """Обработать один файл"""
        file_name = file_path.name

        try:
            ext = file_path.suffix.lower()
            if ext not in READER_REGISTRY:
                raise DataFormatError(f"Неподдерживаемое расширение: {ext}")

            reader_class = READER_REGISTRY[ext]
            reader = reader_class(file_path)
            transactions = reader.read()

            if not transactions:
                logger.warning(f"Файл {file_name} не содержит транзакций")
                self.result.add_success(0)
                return

            try:
                self.validator.validate_currency_consistency(transactions)
            except CurrencyMismatchError as e:
                error = ProcessingError(
                    file_name=file_name,
                    line_number=None,
                    error_type='CurrencyMismatchError',
                    error_message=str(e)
                )
                self.result.errors.append(error)
                logger.error(f"Ошибка валют в файле {file_name}: {e}")
                return

            valid_transactions = []
            validation_errors = []

            for transaction in transactions:
                try:
                    if self.validator.validate(transaction):
                        valid_transactions.append(transaction)
                except (ValidationError, DuplicateIdError) as e:
                    error = ProcessingError(
                        file_name=file_name,
                        line_number=None,
                        error_type=type(e).__name__,
                        error_message=str(e),
                        raw_data={
                            'id': transaction.id,
                            'amount': str(transaction.amount)
                        }
                    )
                    validation_errors.append(error)
                    logger.error(f"Ошибка валидации в файле {file_name}: {e}")

            self.result.errors.extend(validation_errors)

            if valid_transactions:
                self.aggregator.add_transactions(valid_transactions)
                self.result.add_success(len(valid_transactions))
                logger.debug(
                    f"Файл {file_name}: обработано "
                    f"{len(valid_transactions)}/{len(transactions)} транзакций"
                )
            else:
                self.result.add_success(0)
                logger.warning(
                    f"Файл {file_name} не содержит валидных транзакций"
                )

        except DataFormatError as e:
            error = ProcessingError(
                file_name=file_name,
                line_number=None,
                error_type='DataFormatError',
                error_message=str(e)
            )
            self.result.errors.append(error)
            logger.error(f"Ошибка формата файла {file_name}: {e}")

        except Exception as e:
            error = ProcessingError(
                file_name=file_name,
                line_number=None,
                error_type='UnexpectedError',
                error_message=str(e)
            )
            self.result.errors.append(error)
            logger.exception(
                f"Неожиданная ошибка при обработке файла {file_name}: {e}"
            )

    def _save_result(self) -> None:
        """Сохранить результат с транзакционной записью"""
        output_data = {
            'summary': {
                'total_files': self.result.total_files,
                'successful_files': self.result.successful_files,
                'failed_files': self.result.failed_files,
                'total_transactions': self.result.total_transactions,
                'valid_transactions': self.result.valid_transactions
            },
            'aggregated_by_category': self.result.aggregated_data,
            'all_valid_transactions': [
                t.to_dict() for t in self.aggregator.get_all_transactions()
            ],
            'errors': [
                {
                    'file': e.file_name,
                    'line': e.line_number,
                    'type': e.error_type,
                    'message': e.error_message,
                    'raw_data': e.raw_data
                }
                for e in self.result.errors
            ]
        }

        temp_file = self.output_file.parent / f"{self.output_file.name}.tmp"

        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            shutil.move(str(temp_file), str(self.output_file))
            logger.debug(f"Результат сохранен в {self.output_file}")

        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            logger.error(f"Ошибка сохранения результата: {e}")
            raise FatalError(f"Не удалось сохранить результат: {e}")

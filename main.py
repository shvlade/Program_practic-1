#!/usr/bin/env python3
"""
Точка входа в приложение
"""

import sys
import argparse
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.services.processor import DataProcessor
from app.core.exceptions import FatalError


def setup_logging(log_file: Path = Path('app.log'), verbose: bool = False):
    """Настройка логирования"""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    try:
        file_handler = logging.FileHandler(
            log_file,
            encoding='utf-8',
            mode='w'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
    except Exception as e:
        print(
            f"Warning: Cannot create log file {log_file}: {e}",
            file=sys.stderr
        )
        file_handler = logging.NullHandler()

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)

    if verbose:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    logging.getLogger('urllib3').setLevel(logging.WARNING)


def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Data Integration Engine - обработка финансовых отчетов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
  python main.py data
  python main.py /path/to/data -o out.json
  python main.py data --log-file mylog.log
  python main.py data --verbose
        """
    )

    parser.add_argument(
        'data_dir',
        type=Path,
        nargs='?',
        default=Path('data'),
        help='Путь к директории с входными файлами (по умолчанию: data)'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        default=Path('result.json'),
        help='Путь к выходному файлу (по умолчанию: result.json)'
    )

    parser.add_argument(
        '--log-file',
        type=Path,
        default=Path('app.log'),
        help='Путь к файлу лога (по умолчанию: app.log)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Показать детальный вывод в консоль'
    )

    return parser.parse_args()


def print_summary(result):
    """Вывод краткой сводки в консоль"""
    print("\n" + "=" * 60)
    print("ОТЧЕТ ОБ ОБРАБОТКЕ")
    print("=" * 60)
    print(f"Всего файлов: {result.total_files}")
    print(f"Успешно обработано: {result.successful_files}")
    print(f"С ошибками: {result.failed_files}")
    print(f"Всего транзакций: {result.total_transactions}")
    print(f"Валидных транзакций: {result.valid_transactions}")

    if result.errors:
        print("\nСПИСОК ОШИБОК:")
        for error in result.errors:
            print(f"  ✗ {error.file_name}: {error.error_type}")
            print(f"    {error.error_message}")

    if result.aggregated_data:
        print("\nАГРЕГАЦИЯ ПО КАТЕГОРИЯМ:")
        sorted_categories = sorted(
            result.aggregated_data.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for category, amount in sorted_categories:
            print(f"  {category}: {amount:>10.2f} RUB")



def main():
    """Основная функция"""
    args = parse_arguments()
    setup_logging(args.log_file, args.verbose)

    logger = logging.getLogger(__name__)

    try:
        processor = DataProcessor(args.data_dir, args.output)
        result = processor.process_all()

        print_summary(result)

        if result.failed_files > 0:
            return 1
        return 0

    except FatalError as e:
        logger.critical(f"Критическая ошибка: {e}")
        print(f"\nКРИТИЧЕСКАЯ ОШИБКА: {e}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        logger.warning("Прерывание пользователем")
        print("\nПрерывание пользователем", file=sys.stderr)
        return 130
    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")
        print(f"\nНЕОБРАБОТАННАЯ ОШИБКА: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

Запуск скрипта
python main.py --files economic1.csv economic2.csv --report kek.csv

Запуск скрипта для тестирования
python -m pytest test_main.py --cov=main --cov-report=term-missing

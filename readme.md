# Главное задание
## Log analyzer
Читает самый свежий по дате лог c пустым расширением или упакованные в qz из папки log.
Дату берет из имени лога.


Анализирует лог и заполняет макет report-$data$.html данными, готовый репорт пишет в папку reports.
Имя репорта содержит дату проанализированного лога.
Если лог уже был проанализирован и с предыдущей операции сохранился репорт, то программа не будет заново читать лог, а просто выходит

### Формат запуска
```
python3 log_analyzer.py [файл конфига]
```

#### Формат файла конфига
Файл конфига - любой файл формата JSON с конфигурацией программы
```
{
    "REPORT_SIZE": 1000, 
    "REPORT_DIR": "./reports", 
    "LOG_DIR": "./log", 
    "ERROR_MAX_RATIO": 0.4, 
    "LOG_FILE": null
}
```
"REPORT_SIZE" - максимальное количество строк в выходном репорте, по умолчанию 1000, 0 - нет ограничения.

"REPORT_DIR" - папка для репортов, по умолчанию "./reports", папка создается, если необходимо

"LOG_DIR" - папка для обрабатываемых логов, по умолчанию "./log"

"ERROR_MAX_RATIO" - доля ошибочных строк в логе, при превышении которого обработка лога останавливается как ошибочного, по умолчанию 0.4

"LOG_FILE" - файл для сохранения вывода программы, по умолчанию null - выводить все в консоль

### Формат запуска тестов
На программу написаны юнит-тесты, запуск тестов:
```
python3 test_log_analyzer.py
```

# Дополнительное задание
## Покер
Реализует алгоритм выбора из 7 карт лучшей руки с 5 картами.

Сделана работа и с джокерами, черным и красным.
### Формат запуска
```
python3 poker.py
```

## Декораторы
Пока не реализовано
# Инвертированный индекс с поддержкой сжатия

Этот проект реализует инвертированный индекс с поддержкой сжатия на основе дельта- и гамма-кодирования Элиаса.

## Установка проекта

1. Склонируйте репозиторий
2. Установите зависимости: 
```bash
pip install -r requirements.txt
```

## Инструкция по использованию

### Индексация документов

#### Без сжатия
```bash
python indexer.py --input urls.txt --output index.json
```

#### Сжатие Gamma
```bash
python indexer.py --input urls.txt --output index.json --compression gamma
```

#### Сжатие Delta
```bash
python indexer.py --input urls.txt --output index.json --compression delta
```

#### Аргументы:
* `--input` - файл со списком URL для индексации
* `--output` - файл для сохранения индекса
* `--compression` - использовать сжатие (gamma, delta)

### Поиск в индексе

```bash
python searcher.py --index index.json --query "Ректор СПбГУ"
```

#### Аргументы:
* `--index` - файл с сохранённым индексом
* `--query` - поисковый запрос

### Тесты

```bash
pytest -v
```

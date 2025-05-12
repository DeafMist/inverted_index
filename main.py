import os.path
import time

from load_documents import load_documents_from_urls
from src.core.document import Document
from src.core.index import InvertedIndex
from src.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Сравнение производительности индекса со сжатием и без"""
    try:
        logger.info("Запуск тестирования производительности индекса")

        # Загрузка документов
        logger.info("Загрузка документов из файла URLs...")
        documents = load_documents_from_urls(os.path.join("data", "internal_links.txt"))

        if not documents:
            logger.error("Документы для тестирования не найдены")
            return

        # Тестирование без сжатия
        logger.info("Запуск теста БЕЗ сжатия...")
        no_compression = run_indexation_test(documents, 'none')

        # Тестирование со сжатием Gamma
        logger.info("Запуск теста СО сжатием Gamma...")
        gamma_compression = run_indexation_test(documents, 'gamma')

        # Вывод результатов
        logger.info("\nРезультаты сравнения:")
        print_results("Без сжатия", no_compression)
        print_results("Gamma сжатие", gamma_compression)

        # Расчёт коэффициентов
        compression_ratio = no_compression['index_size'] / gamma_compression['index_size']
        slowdown_factor = gamma_compression['indexing_time'] / no_compression['indexing_time']

        logger.info(f"\nКоэффициент сжатия: {compression_ratio:.2f}x")
        logger.info(f"Замедление индексации: {slowdown_factor:.2f}x")

    except Exception as e:
        logger.error(f"Ошибка тестирования: {str(e)}", exc_info=True)


def run_indexation_test(documents: list[dict], method: str) -> dict:
    """Запуск одного теста индексации"""
    index = InvertedIndex(compression_method=method)
    start_time = time.time()

    # Индексация документов
    for doc in documents:
        try:
            index.add_document(Document(doc['doc_id'], doc['text'], doc['metadata']))
        except Exception as e:
            logger.debug(f"Ошибка добавления документа {doc['doc_id']}: {str(e)}")
            continue

    indexing_time = time.time() - start_time

    # Расчёт размера индекса
    index_size = sum(
        len(term.encode('utf-8')) + len(encoded_postings)
        for term, encoded_postings in index.index.items()
    )

    # Тест поиска
    search_start = time.time()
    results = index.search("Ректор СПбГУ")
    search_time = time.time() - search_start

    return {
        'indexing_time': indexing_time,
        'index_size': index_size,
        'search_time': search_time,
        'results_count': len(results)
    }


def print_results(label: str, data: dict):
    """Форматированный вывод результатов"""
    logger.info(f"\n{label}:")
    logger.info(f"Время индексации: {data['indexing_time']:.2f} сек")
    logger.info(f"Размер индекса: {data['index_size'] / (1024 * 1024):.2f} МБ")
    logger.info(f"Время поиска: {data['search_time']:.4f} сек")
    logger.info(f"Найдено документов: {data['results_count']}")


if __name__ == "__main__":
    main()

import argparse
import base64
import json

from src.core.document import Document
from src.core.index import InvertedIndex
from src.utils.logger import get_logger

logger = get_logger(__name__)


def load_index(path: str) -> InvertedIndex:
    """Загрузка индекса из JSON"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    index = InvertedIndex(compression_method=data["compression_method"])

    # Декодирование с учетом метода сжатия
    index.index = {
        term: base64.b64decode(encoded_data)
        for term, encoded_data in data["index"].items()
    }

    # Восстановление документов
    index.documents = {
        int(doc_id): Document(
            doc_data["doc_id"],
            doc_data["text"],
            doc_data["metadata"]
        )
        for doc_id, doc_data in data["documents"].items()
    }

    index.term_frequencies = data["term_frequencies"]
    return index


def search_in_index(index_path: str, query: str) -> list[Document]:
    """Выполняет поиск в сохранённом индексе"""
    index = load_index(index_path)
    return index.search(query)


def main():
    """Точка входа для скрипта поиска"""
    parser = argparse.ArgumentParser(description='Поиск по индексу')
    parser.add_argument('--index', required=True, help='Файл индекса')
    parser.add_argument('--query', required=True, help='Поисковый запрос')
    args = parser.parse_args()

    try:
        logger.info(f"Поиск запроса: {args.query}")
        results = search_in_index(args.index, args.query)

        logger.info(f"Найдено документов: {len(results)}")
        for doc in results:
            logger.info(f"ID: {doc.doc_id} | Заголовок: {doc.metadata.get('title', '')}")
            logger.info(f"URL: {doc.metadata.get('url', '')}\n")

    except Exception as e:
        logger.error(f"Ошибка поиска: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()

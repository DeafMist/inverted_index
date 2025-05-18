import argparse
import base64
import json

from load_documents import load_documents_from_urls
from src.core.document import Document
from src.core.index import InvertedIndex
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_index(urls_file: str, compression_method: str) -> InvertedIndex:
    """Загружает документы и строит индекс с выбранным сжатием"""
    documents = load_documents_from_urls(urls_file)
    index = InvertedIndex(compression_method=compression_method)

    for doc in documents:
        try:
            index.add_document(Document(doc['doc_id'], doc['text'], doc['metadata']))
        except Exception as e:
            logger.debug(f"Ошибка добавления документа {doc['doc_id']}: {str(e)}")

    return index


def save_index(index: InvertedIndex, path: str) -> None:
    """Сохранение индекса в JSON с кодированием бинарных данных"""
    # Преобразуем бинарные данные в base64
    index_data = {
        "index": {
            term: base64.b64encode(data).decode("utf-8")
            for term, data in index.index.items()
        },
        "documents": {
            doc_id: {
                "doc_id": doc.doc_id,
                "text": doc.text,
                "metadata": doc.metadata
            }
            for doc_id, doc in index.documents.items()
        },
        "compression_method": index.compression_method,
        "term_frequencies": index.term_frequencies
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)


def main():
    """Точка входа для скрипта индексации"""
    parser = argparse.ArgumentParser(description='Индексатор документов')
    parser.add_argument('--input', required=True, help='Файл со списком URL')
    parser.add_argument('--output', required=True, help='Файл для сохранения индекса')
    parser.add_argument('--compression', choices=['none', 'gamma', 'delta'],
                        default='none', help='Метод сжатия (gamma/delta)')
    args = parser.parse_args()

    try:
        logger.info(f"Начало индексации с методом сжатия: {args.compression}")
        index = build_index(args.input, args.compression)

        save_index(index, args.output)

        logger.info(f"Индекс успешно сохранён в {args.output}")

    except Exception as e:
        logger.error(f"Ошибка индексации: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()

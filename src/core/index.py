from collections import defaultdict

import nltk
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize

from .document import Document
from ..compression.utils import encode_postings, decode_postings
from ..utils.exceptions import IndexationError
from ..utils.logger import get_logger

nltk.download('punkt_tab')
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

logger = get_logger(__name__)


class InvertedIndex:
    """Класс обратного индекса для поисковой системы"""

    def __init__(self, compression_method: str = 'none'):
        self.index: dict[str, bytes] = {}  # Термин -> сжатый список ID
        self.documents: dict[int, Document] = {}  # Хранилище документов
        self.compression_method = compression_method  # Метод сжатия
        self.term_frequencies: dict[str, dict[int, int]] = defaultdict(dict)  # Частоты терминов

    def add_document(self, document: Document) -> None:
        """Добавление документа в индекс"""
        try:
            if document.doc_id in self.documents:
                logger.warning(f"Документ с ID {document.doc_id} уже существует. Перезапись.")

            self.documents[document.doc_id] = document
            terms = self._process_text(document.text)

            for term in terms:
                if term not in self.index:
                    self.index[term] = self._encode_postings([document.doc_id])
                else:
                    current = self._decode_postings(self.index[term])
                    if document.doc_id not in current:
                        current.append(document.doc_id)
                        self.index[term] = self._encode_postings(sorted(current))

                # Обновление частоты термина
                self.term_frequencies[term][document.doc_id] = \
                    self.term_frequencies[term].get(document.doc_id, 0) + 1

        except Exception as e:
            logger.error(f"Ошибка добавления документа {document.doc_id}: {str(e)}")
            raise IndexationError(f"Ошибка индексации: {str(e)}")

    def search(self, query: str) -> list[Document]:
        """Поиск документов, содержащих все термины из запроса"""
        try:
            terms = self._process_text(query)
            if not terms:
                return []

            # Получение списков документов для каждого термина
            postings_sets = []
            for term in terms:
                if term not in self.index:
                    return []  # Если хотя бы один термин не найден
                try:
                    postings = self._decode_postings(self.index[term])
                    postings_sets.append(set(postings))
                except Exception as e:
                    logger.error(f"Ошибка декодирования для термина '{term}': {str(e)}")
                    return []

            # Поиск пересечения всех списков
            result_ids = set(postings_sets[0])
            for s in postings_sets[1:]:
                result_ids.intersection_update(s)

            # Сортировка по частоте терминов (простой ранжинг)
            ranked_ids = sorted(
                result_ids,
                key=lambda doc_id: sum(
                    self.term_frequencies[term].get(doc_id, 0)
                    for term in terms
                ),
                reverse=True
            )

            return [self.documents[doc_id] for doc_id in ranked_ids]

        except Exception as e:
            logger.error(f"Ошибка поиска по запросу '{query}': {str(e)}")
            return []

    @staticmethod
    def _process_text(text: str) -> list[str]:
        """Обработка текста: токенизация, нормализация и стемминг"""
        if not isinstance(text, str):
            return []

        text = text.lower().strip()
        if not text:
            return []

        # Токенизация
        tokens = word_tokenize(text)

        # Удаление стоп-слов и коротких токенов
        stop_words = set(stopwords.words('russian') + stopwords.words('english'))
        tokens = [
            token for token in tokens
            if token.isalnum()
               and len(token) > 2
               and token not in stop_words
        ]

        # Стемминг для русского языка
        stemmer = SnowballStemmer('russian')
        return [stemmer.stem(token) for token in tokens]

    def _encode_postings(self, postings: list[int]) -> bytes:
        """Кодирование списка ID документов с выбранным методом"""
        if self.compression_method == 'none':
            return ",".join(map(str, postings)).encode('utf-8')
        return encode_postings(postings, self.compression_method)

    def _decode_postings(self, encoded: bytes) -> list[int]:
        """Декодирование списка ID документов"""
        if self.compression_method == 'none':
            return [int(doc_id) for doc_id in encoded.decode('utf-8').split(",")]
        return decode_postings(encoded, self.compression_method)

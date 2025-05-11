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
    def __init__(self, use_compression: bool = True):
        self.index: dict[str, bytes] = {}  # term -> compressed postings
        self.documents: dict[int, Document] = {}
        self.use_compression = use_compression
        self.next_doc_id = 0
        self.term_frequencies: dict[str, dict[int, int]] = defaultdict(dict)

    def add_document(self, document: Document) -> None:
        """Add a document to the index"""
        try:
            if document.doc_id in self.documents:
                logger.warning(f"Document with ID {document.doc_id} already exists. Overwriting.")

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

                # Update term frequency
                self.term_frequencies[term][document.doc_id] =\
                    self.term_frequencies[term].get(document.doc_id, 0) + 1

        except Exception as e:
            logger.error(f"Failed to add document {document.doc_id}: {str(e)}")
            raise IndexationError(f"Failed to add document: {str(e)}")

    def search(self, query: str) -> list[Document]:
        """Search for documents containing all terms in the query"""
        try:
            terms = self._process_text(query)
            if not terms:
                return []

            # Get postings for each term
            postings_sets = []
            for term in terms:
                if term not in self.index:
                    return []  # At least one term not found
                try:
                    postings = self._decode_postings(self.index[term])
                    postings_sets.append(set(postings))
                except Exception as e:
                    logger.error(f"Failed to decode postings for term '{term}': {str(e)}")
                    return []

            # Find intersection of all postings sets
            result_ids = set(postings_sets[0])
            for s in postings_sets[1:]:
                result_ids.intersection_update(s)

            # Sort by term frequency (simple ranking)
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
            logger.error(f"Search failed for query '{query}': {str(e)}")
            return []

    def _process_text(self, text: str) -> list[str]:
        """Improved text processing with proper tokenization and normalization"""
        if not isinstance(text, str):
            return []

        text = text.lower().strip()
        if not text:
            return []

        # Tokenize
        tokens = word_tokenize(text)

        # Remove stopwords and short tokens
        stop_words = set(stopwords.words('russian') + stopwords.words('english'))
        tokens = [
            token for token in tokens
            if token.isalnum()
               and len(token) > 2
               and token not in stop_words
        ]

        # Stemming
        stemmer = SnowballStemmer('russian')
        return [stemmer.stem(token) for token in tokens]

    def _encode_postings(self, postings: list[int]) -> bytes:
        """Encode postings list using the configured compression method"""
        if not self.use_compression:
            return ",".join(map(str, postings)).encode('utf-8')
        return encode_postings(postings)

    def _decode_postings(self, encoded: bytes) -> list[int]:
        """Decode postings list using the configured compression method"""
        if not self.use_compression:
            return [int(doc_id) for doc_id in encoded.decode('utf-8').split(",")]
        return decode_postings(encoded)

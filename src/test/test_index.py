from unittest.mock import patch

import pytest

from src.core.document import Document
from src.core.index import InvertedIndex, IndexationError


@patch("src.core.index.encode_postings", return_value=b"encoded")
@patch("nltk.tokenize.word_tokenize", return_value=["this", "is", "test"])
@patch("nltk.corpus.stopwords.words", return_value=["is"])
@patch("nltk.stem.SnowballStemmer.stem", side_effect=lambda w: w)
def test_add_document_updates_index(mock_stem, mock_stopwords, mock_tokenize, mock_encode):
    index = InvertedIndex(compression_method="gamma")
    doc = Document(doc_id=1, text="This is test")
    index.add_document(doc)

    assert 1 in index.documents
    assert "this" in index.index
    assert index.term_frequencies["this"][1] == 1
    mock_encode.assert_called()


@patch("src.core.index.encode_postings", return_value=b"compressed")
@patch("nltk.tokenize.word_tokenize", return_value=["one", "two", "two"])
@patch("nltk.corpus.stopwords.words", return_value=[])
@patch("nltk.stem.SnowballStemmer.stem", side_effect=lambda w: w)
def test_term_frequency_counts(mock_stem, mock_stopwords, mock_tokenize, mock_encode):
    index = InvertedIndex()
    doc = Document(doc_id=2, text="one two two")
    index.add_document(doc)

    assert index.term_frequencies["one"][2] == 1
    assert index.term_frequencies["two"][2] == 2


def test_add_document_raises_indexation_error(monkeypatch):
    index = InvertedIndex()

    def mock_process_text(text):
        raise ValueError("Ошибка обработки текста")

    monkeypatch.setattr(index, "_process_text", mock_process_text)

    doc = Document(1, "Текст")

    with pytest.raises(IndexationError) as exc_info:
        index.add_document(doc)

    assert "Ошибка обработки текста" in str(exc_info.value)


@pytest.fixture
def index():
    idx = InvertedIndex()
    idx.add_document(Document(1, "Кошка сидит на ковре"))
    idx.add_document(Document(2, "Собака гуляет в парке"))
    idx.add_document(Document(3, "Кошка и собака дружат"))
    return idx


def test_search_single_term(index):
    results = index.search("кошка")
    assert len(results) == 2
    assert all("кошка" in doc.text.lower() for doc in results)


def test_search_multiple_terms(index):
    results = index.search("кошка собака")
    assert len(results) == 1
    assert results[0].doc_id == 3


def test_search_term_not_found(index):
    results = index.search("птица")
    assert results == []


def test_search_empty_query(index):
    results = index.search("")
    assert results == []


def test_search_ranking_by_term_frequency():
    idx = InvertedIndex()
    idx.add_document(Document(1, "кот кот кот"))
    idx.add_document(Document(2, "кот кот"))
    idx.add_document(Document(3, "кот"))

    results = idx.search("кот")
    assert results[0].doc_id == 1
    assert results[1].doc_id == 2
    assert results[2].doc_id == 3


@pytest.fixture
def empty_index():
    return InvertedIndex()


def test_process_text_basic(empty_index):
    text = "Кошки и собаки бегают быстро"
    tokens = empty_index._process_text(text)
    assert "кошк" in tokens
    assert "собак" in tokens
    assert "бега" in tokens
    assert "быстр" in tokens
    assert "и" not in tokens  # стоп-слово
    assert all(isinstance(token, str) for token in tokens)


def test_process_text_punctuation_and_stopwords(empty_index):
    text = "Hello, world! This is a test."
    tokens = empty_index._process_text(text)
    assert "hello" in tokens
    assert "world" in tokens
    assert "this" not in tokens
    assert "is" not in tokens
    assert "a" not in tokens


def test_process_text_empty_and_nonstring(empty_index):
    assert empty_index._process_text("") == []
    assert empty_index._process_text(None) == []
    assert empty_index._process_text(123) == []


def test_process_text_case_normalization(empty_index):
    text = "КоШкА"
    tokens = empty_index._process_text(text)
    # Стемминг к "кошк"
    assert tokens == ["кошк"]

from unittest.mock import patch

from indexer import build_index
from src.core.index import InvertedIndex


def mock_documents():
    return [
        {'doc_id': 1, 'text': "Текст первого документа", 'metadata': {'author': 'A'}},
        {'doc_id': 2, 'text': "Второй текст", 'metadata': {'author': 'B'}},
        {'doc_id': 3, 'text': "Некорректный документ", 'metadata': {'author': 'C'}},
    ]


@patch('indexer.load_documents_from_urls')
def test_build_index_success(mock_load):
    mock_load.return_value = mock_documents()

    index = build_index('fake_urls.txt', compression_method='none')

    assert isinstance(index, InvertedIndex)
    assert len(index.documents) == 3
    assert 1 in index.documents
    assert index.documents[1].text == "Текст первого документа"


@patch('indexer.load_documents_from_urls')
def test_build_index_handles_document_error(mock_load):
    docs = [
        {'doc_id': 1, 'text': "Текст", 'metadata': {}},
        {'doc_id': -1, 'text': "Неправильный ID", 'metadata': {}},
        {'doc_id': 2, 'text': "Ещё текст", 'metadata': {}}
    ]
    mock_load.return_value = docs

    index = build_index('fake_urls.txt', compression_method='none')
    assert 1 in index.documents
    assert 2 in index.documents
    assert -1 not in index.documents


@patch('indexer.load_documents_from_urls')
def test_build_index_with_compression(mock_load):
    mock_load.return_value = mock_documents()
    index = build_index('fake_urls.txt', compression_method='delta')
    assert index.compression_method == 'delta'
    assert len(index.documents) == 3

import pytest
from src.core.document import Document


def test_document_valid_initialization():
    doc = Document(doc_id=1, text="Some text", metadata={"author": "Alice"})
    assert doc.doc_id == 1
    assert doc.text == "Some text"
    assert doc.metadata == {"author": "Alice"}


def test_document_default_metadata():
    doc = Document(doc_id=2, text="Another doc")
    assert doc.metadata == {}


def test_document_invalid_doc_id():
    with pytest.raises(ValueError):
        Document(doc_id=-1, text="Invalid")


def test_document_invalid_text_type():
    with pytest.raises(ValueError):
        Document(doc_id=0, text=123)

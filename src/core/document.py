from dataclasses import dataclass

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Document:
    doc_id: int
    text: str
    metadata: dict = None

    def __post_init__(self):
        if not isinstance(self.doc_id, int) or self.doc_id < 0:
            logger.error(f"Invalid document ID: {self.doc_id}")
            raise ValueError("Document ID must be a non-negative integer")

        if not isinstance(self.text, str):
            logger.error(f"Invalid document text type: {type(self.text)}")
            raise ValueError("Document text must be a string")

        if self.metadata is None:
            self.metadata = {}

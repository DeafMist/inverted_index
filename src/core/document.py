from dataclasses import dataclass

from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Document:
    doc_id: int
    text: str
    metadata: dict = None

    def __post_init__(self):
        """Валидация данных при инициализации документа"""
        if not isinstance(self.doc_id, int) or self.doc_id < 0:
            logger.error(f"Некорректный ID документа: {self.doc_id}")
            raise ValueError("ID документа должен быть неотрицательным целым числом")

        if not isinstance(self.text, str):
            logger.error(f"Некорректный тип текста документа: {type(self.text)}")
            raise ValueError("Текст документа должен быть строкой")

        if self.metadata is None:
            self.metadata = {}

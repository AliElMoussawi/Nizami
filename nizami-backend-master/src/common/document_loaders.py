from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document

from src.common.text_extraction import extract_text_from_file


class TextLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self) -> list[Document]:
        text = extract_text_from_file(file_path=self.file_path)
        return [
            Document(
                page_content=text,
                metadata={"source": str(self.file_path)}
            )
        ]

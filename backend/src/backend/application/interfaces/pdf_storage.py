from abc import abstractmethod
from typing import Protocol


class PDFStorage(Protocol):
    @abstractmethod
    async def save(self, pdf_bytes: bytes, filename: str) -> str:
        raise NotImplementedError

    @abstractmethod
    async def get(self, file_id: str) -> tuple[bytes, str] | None:
        raise NotImplementedError

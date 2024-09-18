from abc import abstractmethod
from asyncio import Protocol


class FileManager(Protocol):
    @abstractmethod
    def save(self, payload: bytes, path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, path: str) -> None:
        raise NotImplementedError

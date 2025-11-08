from abc import abstractmethod
from typing import Protocol


class TransactionManager(Protocol):
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

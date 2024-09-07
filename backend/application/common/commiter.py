from abc import abstractmethod
from typing import Protocol


class Commiter(Protocol):
    @abstractmethod
    async def commit(self) -> None: ...

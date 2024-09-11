from abc import abstractmethod
from typing import Generic, TypeVar

InputData = TypeVar("InputData")
OutputData = TypeVar("OutputData")


class Interactor(Generic[InputData, OutputData]):
    @abstractmethod
    async def __call__(self, data: InputData) -> OutputData:
        raise NotImplementedError

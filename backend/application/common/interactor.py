from abc import abstractmethod
from typing import Generic, TypeVar

RequestData = TypeVar("RequestData")
ResponseData = TypeVar("ResponseData")


class Interactor(Generic[RequestData, ResponseData]):
    @abstractmethod
    async def __call__(self, data: RequestData) -> ResponseData:
        raise NotImplementedError

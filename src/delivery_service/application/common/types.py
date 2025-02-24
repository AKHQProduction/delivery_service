from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

ResultType = TypeVar("ResultType", bound=Any)


class Request(Generic[ResultType], ABC): ...


class Command(Request[ResultType]): ...


RequestType = TypeVar("RequestType", bound=Request)


class RequestHandler(Generic[RequestType, ResultType], ABC):
    @abstractmethod
    async def handle(self, request: RequestType) -> ResultType: ...

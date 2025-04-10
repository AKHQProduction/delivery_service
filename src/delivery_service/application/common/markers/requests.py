from dataclasses import dataclass
from typing import Generic, TypeVar

from bazario import Request

TypeResult = TypeVar("TypeResult")


@dataclass(frozen=True)
class BaseCommand(Generic[TypeResult], Request[TypeResult]): ...


@dataclass(frozen=True)
class TelegramRequest(Generic[TypeResult], Request[TypeResult]): ...

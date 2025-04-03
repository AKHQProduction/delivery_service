from dataclasses import dataclass
from typing import Generic, TypeVar

from bazario import Request

TypeResult = TypeVar("TypeResult")


@dataclass(frozen=True)
class Command(Generic[TypeResult], Request[TypeResult]): ...


@dataclass(frozen=True)
class TelegramCommand(Generic[TypeResult], Request[TypeResult]): ...

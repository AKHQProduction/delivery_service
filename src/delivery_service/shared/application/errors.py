from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationError(Exception):
    @property
    def message(self) -> str:
        return "Application error"


@dataclass(eq=False)
class NotFoundError(Exception):
    @property
    def message(self) -> str:
        return "Entity not found"

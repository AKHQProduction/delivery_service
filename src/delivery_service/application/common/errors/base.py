from dataclasses import dataclass


@dataclass(frozen=True)
class ApplicationError(Exception):
    @property
    def message(self) -> str:
        return "Application error"

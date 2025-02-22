from dataclasses import dataclass


@dataclass(eq=False)
class ValidationError(Exception):
    @property
    def message(self) -> str:
        return "Validation error"

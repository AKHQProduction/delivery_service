from dataclasses import dataclass


@dataclass(eq=False)
class DomainError(Exception):
    @property
    def message(self):
        return "Application error"

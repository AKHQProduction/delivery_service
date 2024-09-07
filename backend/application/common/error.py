from dataclasses import dataclass


@dataclass(eq=False)
class ApplicationError(Exception):
    @property
    def message(self):
        return "Application error"

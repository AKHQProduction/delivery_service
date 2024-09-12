from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class AccessDeniedError(ApplicationError):
    @property
    def message(self):
        return "You do not have permission."

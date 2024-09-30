from dataclasses import dataclass

from entities.common.errors import DomainError


@dataclass(eq=False)
class UserIsNotActiveError(DomainError):
    user_id: int

    @property
    def message(self):
        return f"User with id={self.user_id} is not active"

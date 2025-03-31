from dataclasses import dataclass

from entities.common.errors import DomainError


@dataclass(eq=False)
class AdminRoleChangeRestrictedError(DomainError):
    user_id: int

    @property
    def message(self) -> str:
        return f"Cannot change user role with id {self.user_id}"

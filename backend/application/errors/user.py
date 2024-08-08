from dataclasses import dataclass

from backend.application.common.errors.base import ApplicationError


@dataclass(eq=False)
class UserIsNotExistError(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"User is not exists with id {self.user_id}"


@dataclass(eq=False)
class UserAlreadyExistsError(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"User already exists with id {self.user_id}"

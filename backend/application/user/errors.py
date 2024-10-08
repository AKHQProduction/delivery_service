from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class UserNotFoundError(ApplicationError):
    user_id: int | None = None

    @property
    def message(self):
        return f"User is not exists with id {self.user_id}"


@dataclass(eq=False)
class UserAlreadyExistError(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"User already exists with id {self.user_id}"

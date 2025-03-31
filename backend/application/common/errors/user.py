from dataclasses import dataclass

from application.common.errors.base import ApplicationError


@dataclass(eq=False)
class UserNotFoundError(ApplicationError):
    user_id: int | None = None

    @property
    def message(self):
        return f"User is not exists with id {self.user_id}"


@dataclass(eq=False)
class UserAlreadyExistsError(ApplicationError):
    phone_number: str

    @property
    def message(self):
        return (
            f"User already exists with this phone number {self.phone_number}"
        )

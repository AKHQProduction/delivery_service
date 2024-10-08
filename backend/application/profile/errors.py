from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class ProfileAlreadyExistError(ApplicationError):
    profile_id: int

    @property
    def message(self):
        return f"Profile with id={self.profile_id} already exists"


@dataclass(eq=False)
class ProfileNotFoundError(ApplicationError):
    user_id: int

    @property
    def message(self):
        return f"Profile for user id={self.user_id} not found"

from dataclasses import dataclass

from application.common.error import ApplicationError


@dataclass(eq=False)
class ProfileAlreadyExistError(ApplicationError):
    profile_id: int

    @property
    def message(self):
        return f"Profile with id={self.profile_id} already exists"

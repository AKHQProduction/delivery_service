from dataclasses import dataclass

from delivery_service.shared.application.errors import EntityAlreadyExistsError


@dataclass(eq=False)
class UserAlreadyExistsError(EntityAlreadyExistsError):
    pass

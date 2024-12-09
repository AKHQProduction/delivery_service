from application.user.errors import UserNotFoundError
from entities.user.errors import UserIsNotActiveError
from entities.user.models import User


def validate_user(user: User | None, *, must_be_active: bool = True):
    if not user:
        raise UserNotFoundError()
    if must_be_active and not user.is_active:
        raise UserIsNotActiveError(user.oid)

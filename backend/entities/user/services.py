from entities.user.models import User


def create_user(
    full_name: str, username: str, tg_id: int | None = None
) -> User:
    return User(
        user_id=None, full_name=full_name, username=username, tg_id=tg_id
    )

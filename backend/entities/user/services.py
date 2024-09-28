from entities.user.models import User, UserId


def create_user(user_id: UserId, full_name: str, username: str) -> User:
    return User(user_id=user_id, full_name=full_name, username=username)

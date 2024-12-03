from entities.user.models import User
from entities.user.value_objects import PhoneNumber, UserAddress


def create_user(
    full_name: str,
    username: str | None = None,
    tg_id: int | None = None,
    phone_number: PhoneNumber | None = None,
    address: UserAddress | None = None,
) -> User:
    return User(
        user_id=None,
        full_name=full_name,
        username=username,
        tg_id=tg_id,
        user_address=address,
        phone_number=phone_number,
    )

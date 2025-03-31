from entities.common.tracker import Tracker
from entities.user.models import User
from entities.user.value_objects import UserAddress


class UserService:
    def __init__(self, tracker: Tracker):
        self.tracker = tracker

    def create_new_user(
        self,
        full_name: str,
        username: str | None = None,
        tg_id: int | None = None,
        phone_number: str | None = None,
        address: UserAddress | None = None,
    ) -> User:
        new_user = User(
            oid=None,
            full_name=full_name,
            username=username,
            tg_id=tg_id,
            user_address=address,
            phone_number=phone_number,
        )

        self.tracker.add_one(new_user)

        return new_user

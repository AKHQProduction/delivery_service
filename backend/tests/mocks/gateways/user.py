from application.common.request_data import Pagination
from application.user.gateway import GetUsersFilters, UserReader, UserSaver
from entities.user.models import User, UserId


class FakeUserGateway(UserReader, UserSaver):
    def __init__(self, user: User):
        self.user = user
        self.users = [self.user]
        self.saved = False

    async def by_id(self, user_id: UserId) -> User | None:
        if self.user.user_id != user_id:
            return None

        return self.user

    async def all(
            self,
            filters: GetUsersFilters,
            pagination: Pagination
    ) -> list[User]:
        return self.users

    async def total_users(
            self,
            filters: GetUsersFilters
    ) -> int:
        return len(self.users)

    async def save(self, user: User) -> None:
        self.saved = True

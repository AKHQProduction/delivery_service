from application.common.persistence import Pagination, UserGateway
from application.user.errors import UserAlreadyExistError
from application.user.gateways import GetUsersFilters
from entities.user.models import User, UserId


class FakeUserGateway(UserGateway):
    def __init__(self):
        self.users: dict[int, User] = {
            1: User(user_id=UserId(1), full_name="First User"),
            2: User(user_id=UserId(2), full_name="Second User"),
            3: User(user_id=UserId(3), full_name="Third User"),
        }

        self.saved = False

    async def by_id(self, user_id: UserId) -> User | None:
        return self.users.get(user_id, None)

    async def all(
        self, filters: GetUsersFilters, pagination: Pagination
    ) -> list[User]:
        users = self.users.values()

        return list(users)

    async def total(self, filters: GetUsersFilters) -> int:
        return len(self.users)

    async def save(self, user: User) -> None:
        user_in_memory = await self.by_id(user.user_id)

        if not user_in_memory:
            self.saved = True
            self.users[user.user_id] = user
        else:
            raise UserAlreadyExistError(user.user_id)

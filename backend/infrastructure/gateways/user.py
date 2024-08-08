from backend.application.common.gateways.user import UserSaver, UserReader
from backend.application.dto import UserDTO
from backend.application.errors.user import UserAlreadyExistsError
from backend.domain.entities.user import User
from backend.domain.value_objects.user_id import UserId


class InMemoryUserGateway(UserReader, UserSaver):
    def __init__(self):
        self.users = {}

    def _get_from_memory(self, user_id: UserId) -> User | None:
        return self.users.get(user_id)

    async def save(self, user: User) -> UserDTO:
        user_in_memory = self._get_from_memory(user.user_id)

        if user_in_memory:
            raise UserAlreadyExistsError(user.user_id.to_raw())

        self.users[user.user_id.to_raw()] = user

        return UserDTO(
            user_id=user.user_id.to_raw(),
            full_name=user.full_name,
            username=user.username,
            phone_number=user.phone_number
        )

    async def by_id(self, user_id: UserId) -> User | None:
        return self._get_from_memory(user_id)

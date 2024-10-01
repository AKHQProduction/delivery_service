from abc import abstractmethod
from asyncio import Protocol

from entities.profile.models import Profile
from entities.user.models import UserId


class ProfileSaver(Protocol):
    @abstractmethod
    async def save(self, profile: Profile) -> None:
        raise NotImplementedError


class ProfileReader(Protocol):
    @abstractmethod
    async def by_identity(self, user_id: UserId) -> Profile | None:
        raise NotImplementedError

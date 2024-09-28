from abc import abstractmethod
from asyncio import Protocol

from entities.profile.models import Profile


class ProfileSaver(Protocol):
    @abstractmethod
    async def save(self, profile: Profile) -> None:
        raise NotImplementedError()

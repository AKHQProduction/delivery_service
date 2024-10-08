from abc import abstractmethod
from asyncio import Protocol

from entities.profile.models import Profile
from entities.shop.models import ShopId
from entities.user.models import UserId


class ProfileSaver(Protocol):
    @abstractmethod
    async def save(self, profile: Profile) -> None:
        raise NotImplementedError


class ProfileReader(Protocol):
    @abstractmethod
    async def by_identity(self, user_id: UserId) -> Profile | None:
        raise NotImplementedError

    @abstractmethod
    async def by_shop_id(
        self, user_id: UserId, shop_id: ShopId
    ) -> Profile | None:
        raise NotImplementedError

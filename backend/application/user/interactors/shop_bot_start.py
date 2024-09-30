from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.profile.gateway import ProfileSaver
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopReader
from application.user.gateway import UserSaver
from entities.profile.services import create_user_profile
from entities.profile.value_objects import UserAddress
from entities.shop.models import ShopId
from entities.shop.services import add_user_to_shop
from entities.user.models import UserId
from entities.user.services import create_user


@dataclass(frozen=True)
class UserAddressData:
    city: str
    street: str
    house_number: int
    apartment_number: int | None
    floor: int | None
    intercom_code: int | None


@dataclass(frozen=True)
class ShopBotStartInputData:
    shop_id: int
    user_id: int
    full_name: str
    username: str | None
    address: UserAddressData | None


class ShopBotStart(Interactor[ShopBotStartInputData, UserId]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_saver: UserSaver,
        profile_saver: ProfileSaver,
        shop_reader: ShopReader,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._user_saver = user_saver
        self._profile_saver = profile_saver
        self._shop_reader = shop_reader
        self._commiter = commiter

    async def __call__(self, data: ShopBotStartInputData) -> UserId:
        actor = await self._identity_provider.get_user()

        if actor:
            return actor.user_id

        user = create_user(
            UserId(data.user_id),
            full_name=data.full_name,
            username=data.username,
        )

        shop = await self._shop_reader.by_id(ShopId(data.shop_id))

        if not shop:
            raise ShopNotFoundError(data.shop_id)

        if not shop.is_active:
            raise ShopIsNotActiveError(data.shop_id)

        add_user_to_shop(shop, user)

        user_address = (
            UserAddress(
                city=data.address.city,
                street=data.address.street,
                house_number=data.address.house_number,
                apartment_number=data.address.apartment_number,
                floor=data.address.floor,
                intercom_code=data.address.intercom_code,
            )
            if data.address
            else None
        )

        profile = create_user_profile(
            shop_id=shop.shop_id, address=user_address, user_id=user.user_id
        )

        await self._user_saver.save(user)
        await self._profile_saver.save(profile)

        await self._commiter.commit()

        return user.user_id

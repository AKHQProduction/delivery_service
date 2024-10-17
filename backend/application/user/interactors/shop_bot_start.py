import logging
from dataclasses import dataclass

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.profile.gateway import ProfileReader, ProfileSaver
from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from application.shop.gateway import ShopGateway
from application.user.gateway import UserSaver
from entities.profile.services import create_user_profile
from entities.shop.models import ShopId
from entities.shop.services import add_user_to_shop
from entities.user.models import UserId
from entities.user.services import create_user


@dataclass(frozen=True)
class ShopBotStartInputData:
    shop_id: int
    user_id: int
    full_name: str
    username: str | None


class ShopBotStart(Interactor[ShopBotStartInputData, UserId]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_saver: UserSaver,
        profile_saver: ProfileSaver,
        profile_reader: ProfileReader,
        shop_reader: ShopGateway,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._user_saver = user_saver
        self._profile_saver = profile_saver
        self._profile_reader = profile_reader
        self._shop_reader = shop_reader
        self._commiter = commiter

    async def __call__(self, data: ShopBotStartInputData) -> UserId:
        actor = await self._identity_provider.get_user()
        if actor:
            profile = await self._profile_reader.by_identity(actor.user_id)

            if not profile.shop_id:
                logging.info(
                    "New profile created to user_id=%s", actor.user_id
                )
                profile.shop_id = data.shop_id

                await self._commiter.commit()

            return actor.user_id

        user = create_user(
            UserId(data.user_id),
            full_name=data.full_name,
            username=data.username,
        )

        logging.info("New user created, with_id=%s", user.user_id)

        shop = await self._shop_reader.by_id(ShopId(data.shop_id))
        if not shop:
            raise ShopNotFoundError(data.shop_id)
        if not shop.is_active:
            raise ShopIsNotActiveError(data.shop_id)

        add_user_to_shop(shop, user)

        profile = create_user_profile(
            user_id=user.user_id,
            shop_id=shop.shop_id,
            address=None,
        )

        await self._user_saver.save(user)
        await self._profile_saver.save(profile)

        await self._commiter.commit()

        return user.user_id

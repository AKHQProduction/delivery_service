import logging
from dataclasses import dataclass, field

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.specification import Specification
from application.shop.gateway import ShopSaver
from application.shop.token_verifier import TokenVerifier
from application.specs.has_role import HasRoleSpec
from application.user.gateway import UserSaver
from application.errors.access import AccessDeniedError
from entities.shop.model import Shop, ShopId
from entities.shop.value_objects import RegularDaysOff, ShopTitle, ShopToken
from entities.user.model import RoleName


@dataclass(frozen=True)
class CreateShopDTO:
    shop_id: int
    title: str
    token: str
    regular_days_off: list[int] = field(default_factory=list)


class CreateShop(Interactor[CreateShopDTO, ShopId]):
    def __init__(
            self,
            shop_saver: ShopSaver,
            user_saver: UserSaver,
            commiter: Commiter,
            identity_provider: IdentityProvider,
            token_verifier: TokenVerifier,
    ) -> None:
        self._shop_saver = shop_saver
        self._user_saver = user_saver
        self._commiter = commiter
        self._identity_provider = identity_provider
        self._token_verifier = token_verifier

    async def __call__(self, data: CreateShopDTO) -> ShopId:
        user = await self._identity_provider.get_user()

        token = ShopToken(data.token)

        await self._token_verifier.verify_token(token)

        shop_id = ShopId(data.shop_id)

        shop = Shop(
                shop_id=shop_id,
                title=ShopTitle(data.title),
                token=ShopToken(data.token),
                regular_days_off=RegularDaysOff(data.regular_days_off)
        )

        await self._shop_saver.save(shop)

        shop.users.append(user)

        await self._commiter.commit()

        logging.info(f"CreateShop: New shop created with id={data.shop_id}")
        logging.info(f"CreateShop: Add user={user.user_id} to shop={shop_id}")

        return shop_id

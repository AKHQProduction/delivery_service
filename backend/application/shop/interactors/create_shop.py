import logging
from dataclasses import dataclass, field

from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.common.specification import Specification
from application.errors.access import AccessDeniedError
from application.shop.gateway import ShopSaver
from application.shop.token_verifier import TokenVerifier
from application.specs.has_role import HasRoleSpec
from application.user.gateways.user import UserSaver
from domain.shop.entity.entity import ShopId
from domain.shop.entity.value_objects import ShopTitle, ShopToken
from domain.shop.service import ShopService
from domain.user.entity.user import RoleName


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

        rule: Specification = HasRoleSpec(RoleName.USER)

        if not rule.is_satisfied_by(user.role):
            logging.info(
                    "CreateShop: access denied for user with "
                    f"id={user.user_id.to_raw()}"
            )
            raise AccessDeniedError()

        token = ShopToken(data.token)

        await self._token_verifier.verify_token(token)

        shop = ShopService.create_shop(
                ShopId(data.shop_id),
                user,
                ShopTitle(data.title),
                token,
                data.regular_days_off
        )

        await self._shop_saver.save(shop)

        logging.info(f"CreateShop: New shop created with id={data.shop_id}")

        logging.info(
                f"CreateShop: Change user={user.user_id} role "
                "to ADMIN"
        )

        await self._commiter.commit()

        return shop.shop_id

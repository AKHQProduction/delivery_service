import logging
from dataclasses import dataclass

from backend.application.errors import AuthorizationError
from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyShopGateway

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MeUser:
    user_id: UserId
    full_name: str | None
    role: ShopRole | None


@dataclass(frozen=True)
class MeShop:
    shop_id: ShopId
    name: str | None
    city: str | None
    street: str | None
    house: str | None


@dataclass(frozen=True)
class GetMeResponse:
    user: MeUser
    shop: MeShop | None


class GetMeQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> None:
        self._idp = idp
        self._shop_gateway = shop_gateway

    async def handle(self) -> GetMeResponse:
        user_id = await self._idp.current_user_id()
        if not user_id:
            raise AuthorizationError

        membership = await self._shop_gateway.load_membership(user_id)

        if not membership:
            logger.info("User has no shop membership: user_id=%s", user_id)
            return GetMeResponse(
                user=MeUser(user_id=user_id, full_name=None, role=None),
                shop=None,
            )

        shop = await self._shop_gateway.load_shop(membership.shop_id)
        logger.info(
            "Loaded user with shop: user_id=%s, shop_id=%s",
            user_id,
            membership.shop_id,
        )

        return GetMeResponse(
            user=MeUser(
                user_id=user_id,
                full_name=membership.name,
                role=ShopRole(membership.role.name),
            ),
            shop=MeShop(
                shop_id=membership.shop_id,
                name=shop.name if shop else None,
                city=shop.city if shop else None,
                street=shop.street if shop else None,
                house=shop.house if shop else None,
            ),
        )

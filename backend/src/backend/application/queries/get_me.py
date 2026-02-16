from dataclasses import dataclass

from backend.application.vars import ShopId, ShopRole, UserId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyShopGateway


@dataclass(frozen=True)
class MeUser:
    user_id: UserId
    full_name: str
    role: ShopRole


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
    shop: MeShop


class GetMeQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        shop_gateway: SQLAlchemyShopGateway,
    ) -> None:
        self._idp = idp
        self._shop_gateway = shop_gateway

    async def handle(self) -> GetMeResponse:
        current_user = await self._idp.current_user()
        shop = await self._shop_gateway.load_shop(current_user.shop_id)

        return GetMeResponse(
            user=MeUser(
                user_id=current_user.user_id,
                full_name=current_user.full_name,
                role=current_user.role,
            ),
            shop=MeShop(
                shop_id=current_user.shop_id,
                name=shop.name if shop else None,
                city=shop.city if shop else None,
                street=shop.street if shop else None,
                house=shop.house if shop else None,
            ),
        )

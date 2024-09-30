from entities.common.token_verifier import TokenVerifier
from entities.shop.models import Shop, ShopId
from entities.shop.value_objects import (
    DeliveryDistance,
    RegularDaysOff,
    ShopLocation,
    ShopTitle,
    ShopToken,
)
from entities.user.errors import UserIsNotActiveError
from entities.user.models import User


class ShopService:
    def __init__(self, token_verifier: TokenVerifier):
        self._token_verifier = token_verifier

    async def create_shop(
        self,
        user: User,
        title: str,
        token: str,
        regular_days_off: list[int],
        delivery_distance: int,
        location: tuple[float, float],
    ) -> Shop:
        shop_id = ShopId(int(token.split(":")[0]))
        title = ShopTitle(title)
        token = ShopToken(token)
        delivery_distance = DeliveryDistance(delivery_distance)
        location = ShopLocation(latitude=location[0], longitude=location[1])
        regular_days_off = RegularDaysOff(regular_days=regular_days_off)

        await self._token_verifier.verify_token(token)

        if not user.is_active:
            raise UserIsNotActiveError(user.user_id)

        shop = Shop(
            shop_id=shop_id,
            title=title,
            token=token,
            delivery_distance=delivery_distance,
            location=location,
            regular_days_off=regular_days_off,
        )

        add_user_to_shop(shop, user)

        return shop


def add_user_to_shop(shop: Shop, user: User) -> None:
    shop.users.append(user)

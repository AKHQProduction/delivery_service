from entities.common.token_verifier import TokenVerifier
from entities.shop.models import Shop, ShopId
from entities.shop.value_objects import RegularDaysOff, ShopTitle, ShopToken
from entities.user.errors import UserIsNotActiveError
from entities.user.models import User


class ShopService:
    def __init__(self, token_verifier: TokenVerifier):
        self._token_verifier = token_verifier

    async def create_shop(
        self,
        user: User,
        shop_id: int,
        title: str,
        token: str,
        regular_days_off: list[int],
    ) -> Shop:
        shop_id = ShopId(shop_id)
        title = ShopTitle(title)
        token = ShopToken(token)
        regular_days_off = RegularDaysOff(regular_days_off)

        await self._token_verifier.verify_token(token)

        if not user.is_active:
            raise UserIsNotActiveError(user.user_id)

        shop = Shop(
            shop_id=shop_id,
            title=title,
            token=token,
            regular_days_off=regular_days_off,
        )

        shop.users.append(user)

        return shop

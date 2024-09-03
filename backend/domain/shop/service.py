from domain.shop.entity.entity import Shop, ShopId
from domain.shop.entity.value_objects import ShopTitle, ShopToken
from domain.user.entity.user import RoleName, User


class ShopService:

    @staticmethod
    def create_shop(
            shop_id: ShopId,
            user: User,
            title: ShopTitle,
            token: ShopToken,
            regular_days_off: list[int]
    ) -> Shop:
        user.role = RoleName.ADMIN

        return Shop(
                shop_id=shop_id,
                user_id=user.user_id,
                title=title,
                token=token,
                regular_days_off=regular_days_off
        )

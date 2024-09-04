from entities.shop.models.entity import Shop
from entities.user.models.user import User


class ShopService:
    @staticmethod
    def change_regular_days_off(
            shop: Shop,
            user: User,
            new_regular_days_off: list[int]
    ) -> None:


        shop.regular_days_off = new_regular_days_off

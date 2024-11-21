from entities.shop.models import Shop, ShopId
from entities.shop.value_objects import (
    DeliveryDistance,
    RegularDaysOff,
    ShopLocation,
    ShopTitle,
    ShopToken,
)
from entities.user.models import User


def create_shop(
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

    shop = Shop(
        shop_id=shop_id,
        title=title,
        token=token,
        delivery_distance=delivery_distance,
        location=location,
        regular_days_off=regular_days_off,
    )

    return shop


def add_user_to_shop(shop: Shop, new_user: User) -> None:
    if new_user not in shop.users:
        shop.users.append(new_user)

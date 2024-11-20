from application.shop.errors import ShopIsNotActiveError, ShopNotFoundError
from entities.shop.models import Shop


def validate_shop(shop: Shop | None, *, must_be_active: bool = True):
    if not shop:
        raise ShopNotFoundError()
    if must_be_active and not shop.is_active:
        raise ShopIsNotActiveError()

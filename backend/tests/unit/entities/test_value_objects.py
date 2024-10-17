from decimal import Decimal

import pytest

from entities.common.errors import InvalidPriceError
from entities.goods.errors import (
    GoodsTitleTooLongError,
    GoodsTitleTooShortError,
)
from entities.goods.value_objects import GoodsPrice, GoodsTitle
from entities.shop.errors import (
    InvalidBotTokenError,
    InvalidRegularDayOffError,
    ShopTitleTooLongError,
    ShopTitleTooShortError,
)
from entities.shop.value_objects import (
    RegularDaysOff,
    ShopTitle,
    ShopToken,
)


@pytest.mark.entities
@pytest.mark.value_objects
@pytest.mark.parametrize(
    ["shop_token", "exc_class"],
    [
        ("1234567898:AAGzbSDaSqQ-mOQEJfPLE1wBH0Y4J40xT48", None),
        ("abc", InvalidBotTokenError),
    ],
)
def test_shop_token(shop_token: str, exc_class) -> None:
    if exc_class:
        with pytest.raises(exc_class):
            ShopToken(shop_token)
    else:
        token = ShopToken(shop_token)

        assert shop_token == token.value
        assert isinstance(token, ShopToken)


@pytest.mark.entities
@pytest.mark.value_objects
@pytest.mark.parametrize(
    ["shop_title", "exc_class"],
    [
        ("TestShop", None),
        ("Ttt", ShopTitleTooShortError),
        ("A" * 21, ShopTitleTooLongError),
    ],
)
def test_shop_title(shop_title: str, exc_class) -> None:
    if exc_class:
        with pytest.raises(exc_class):
            ShopTitle(shop_title)
    else:
        title = ShopTitle(shop_title)

        assert shop_title == title.title
        assert isinstance(title, ShopTitle)


@pytest.mark.entities
@pytest.mark.value_objects
@pytest.mark.parametrize(
    ["regular_days_off", "exc_class"],
    [
        ([], None),
        ([2, 5], None),
        ([-1, 3, 5], InvalidRegularDayOffError),
        ([7, 5, 3], InvalidRegularDayOffError),
    ],
)
def test_regular_days_off(regular_days_off: list[int], exc_class) -> None:
    if exc_class:
        with pytest.raises(exc_class):
            RegularDaysOff(regular_days_off)
    else:
        days_off = RegularDaysOff(regular_days_off)

        assert days_off.regular_days == regular_days_off
        assert isinstance(days_off, RegularDaysOff)


@pytest.mark.entities
@pytest.mark.value_objects
@pytest.mark.parametrize(
    ["goods_title", "exc_class"],
    [
        ("TestTitle", None),
        ("", GoodsTitleTooShortError),
        ("A" * 21, GoodsTitleTooLongError),
    ],
)
def test_goods_title(goods_title: str, exc_class) -> None:
    if exc_class:
        with pytest.raises(exc_class):
            GoodsTitle(goods_title)
    else:
        title = GoodsTitle(goods_title)

        assert goods_title == title.title
        assert isinstance(title, GoodsTitle)


@pytest.mark.entities
@pytest.mark.value_objects
@pytest.mark.parametrize(
    ["value", "exc_class"],
    [
        ("2.50", None),
        ("0", InvalidPriceError),
        ("-2.50", InvalidPriceError),
        (2.50, None),
    ],
)
def test_goods_price(value: Decimal, exc_class) -> None:
    if exc_class:
        with pytest.raises(exc_class):
            GoodsPrice(value)
    else:
        price = GoodsPrice(value)

        assert Decimal(value) == price.value
        assert isinstance(price, GoodsPrice)

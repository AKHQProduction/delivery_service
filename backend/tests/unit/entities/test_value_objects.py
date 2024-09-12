from datetime import datetime, timedelta

import pytest
from zoneinfo import ZoneInfo

from entities.shop.errors import (
    InvalidBotTokenError,
    InvalidRegularDayOffError,
    InvalidSpecialDayOffError,
    ShopTitleTooLongError,
    ShopTitleTooShortError,
)
from entities.shop.value_objects import (
    RegularDaysOff,
    ShopTitle,
    ShopToken,
    SpecialDaysOff,
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

        assert days_off.days == regular_days_off
        assert isinstance(days_off, RegularDaysOff)


@pytest.mark.entities
@pytest.mark.value_objects
@pytest.mark.parametrize(
    ["special_days_off", "exc_class"],
    [
        ([datetime.now(ZoneInfo("Europe/Kiev")) + timedelta(days=1)], None),
        (
            [datetime.now(ZoneInfo("Europe/Kiev")) - timedelta(days=1)],
            InvalidSpecialDayOffError,
        ),
        ([], None),
    ],
)
def test_special_days_off(special_days_off: list[datetime], exc_class) -> None:
    if exc_class:
        with pytest.raises(exc_class):
            SpecialDaysOff(special_days_off)
    else:
        days_off = SpecialDaysOff(special_days_off)

        assert days_off.days == special_days_off
        assert isinstance(days_off, SpecialDaysOff)

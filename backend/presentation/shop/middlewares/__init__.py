from aiogram import Dispatcher

from .shop_id import ShopIdMiddleware


def setup_shop_bot_middlewares(dp: Dispatcher) -> None:
    dp.update.outer_middleware(ShopIdMiddleware())

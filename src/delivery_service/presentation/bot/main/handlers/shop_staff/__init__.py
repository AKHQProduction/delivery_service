from aiogram import Dispatcher

from .products_flow import PRODUCTS_ROUTER


def setup_shop_staff_handler(dp: Dispatcher) -> None:
    dp.include_router(PRODUCTS_ROUTER)

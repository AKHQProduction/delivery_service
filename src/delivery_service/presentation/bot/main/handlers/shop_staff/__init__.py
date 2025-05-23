from aiogram import Dispatcher

from .customers_flow import (
    ADDRESS_DATA_ENTRY_DIALOG,
    CUSTOMERS_DIALOG,
    CUSTOMERS_ROUTER,
)
from .orders_flow import ORDERS_DIALOG, ORDERS_ROUTER
from .products_flow import PRODUCTS_DIALOG, PRODUCTS_ROUTER
from .staff_flow import STAFF_DIALOG, STAFF_ROUTER


def setup_shop_staff_handler(dp: Dispatcher) -> None:
    dp.include_router(PRODUCTS_ROUTER)
    dp.include_router(STAFF_ROUTER)
    dp.include_router(CUSTOMERS_ROUTER)
    dp.include_router(ORDERS_ROUTER)


def setup_shop_staff_dialogs(dp: Dispatcher) -> None:
    dp.include_router(PRODUCTS_DIALOG)
    dp.include_router(STAFF_DIALOG)
    dp.include_router(CUSTOMERS_DIALOG)
    dp.include_router(ADDRESS_DATA_ENTRY_DIALOG)
    dp.include_router(ORDERS_DIALOG)

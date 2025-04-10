from aiogram import F, Router
from aiogram.types import Message

from delivery_service.infrastructure.integration.telegram.const import (
    PRODUCTS_BTN,
)

PRODUCTS_ROUTER = Router()


@PRODUCTS_ROUTER.message(F.text == PRODUCTS_BTN)
async def add_new_product(_: Message) -> None:
    pass

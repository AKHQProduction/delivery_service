from aiogram import F, Router
from aiogram.types import Message
from bazario.asyncio import Sender
from dishka import FromDishka

from delivery_service.application.commands.add_new_product import (
    AddNewProductRequest,
)
from delivery_service.domain.products.product import ProductType
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.infrastructure.integration.telegram.const import (
    PRODUCTS_BTN,
)

PRODUCTS_ROUTER = Router()


@PRODUCTS_ROUTER.message(F.text == PRODUCTS_BTN)
async def add_new_product(
    message: Message, sender: FromDishka[Sender]
) -> None:
    await sender.send(
        AddNewProductRequest(
            title="SecondTestProduct",
            price=FixedDecimal(100),
            product_type=ProductType.ACCESSORIES,
        )
    )

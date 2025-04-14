from aiogram import F, Router
from aiogram.types import Message
from bazario.asyncio import Sender
from dishka import FromDishka

from delivery_service.application.commands.add_new_customer import (
    AddNewCustomerRequest,
)
from delivery_service.infrastructure.integration.telegram.const import (
    CUSTOMERS_BTN,
)

CUSTOMERS_ROUTER = Router()


@CUSTOMERS_ROUTER.message(F.text == CUSTOMERS_BTN)
async def launch_customer_dialog(_: Message, sender: FromDishka[Sender]):
    await sender.send(
        AddNewCustomerRequest(full_name="AAA", phone_number="+380980000000")
    )

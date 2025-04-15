from typing import Any

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Case, Const, Format
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.query.customer import GetAllCustomersRequest
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.integration.telegram.const import (
    CUSTOMERS_BTN,
)
from delivery_service.presentation.bot.widgets.kbd import get_back_btn

from .states import CustomerMenu

CUSTOMERS_ROUTER = Router()


@CUSTOMERS_ROUTER.message(F.text == CUSTOMERS_BTN)
async def launch_customer_dialog(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=CustomerMenu.MAIN, mode=StartMode.RESET_STACK
    )


def get_customer_id(manager: DialogManager) -> UserID:
    customer_id_str = manager.dialog_data.get("customer_id")
    if not customer_id_str:
        raise ValueError()

    return UserID(customer_id_str)


@inject
async def get_all_shop_customers(
    sender: FromDishka[Sender], **_kwargs
) -> dict[str, Any]:
    response = await sender.send(GetAllCustomersRequest())

    return {"customers": response.customers, "total": response.total}


@inject
async def get_shop_customer(
    dialog_manager: DialogManager,
    customer_reader: FromDishka[CustomerGateway],
    **_kwargs,
) -> dict[str, Any]:
    customer_id = get_customer_id(dialog_manager)
    customer = await customer_reader.read_with_id(customer_id)
    if not customer:
        raise ValueError()

    return {
        "full_name": customer.full_name,
        "phone": customer.primary_phone,
        "address": f"{customer.delivery_address.city}, "
        f"{customer.delivery_address.street} "
        f"{customer.delivery_address.house_number}",
        "is_private_home": bool(customer.delivery_address.floor is not None),
        "has_intercom_code": bool(customer.delivery_address.intercom_code),
        "apartment_number": customer.delivery_address.apartment_number,
        "floor": customer.delivery_address.floor,
        "intercom_code": customer.delivery_address.intercom_code,
    }


async def on_select_shop_customer(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["customer_id"] = value
    await manager.switch_to(state=CustomerMenu.CUSTOMER_CARD)


CUSTOMERS_DIALOG = Dialog(
    Window(
        Const("<b>Меню клієнтів</b>"),
        ScrollingGroup(
            Select(
                id="customer_item",
                items="customers",
                item_id_getter=lambda item: item.customer_id,
                text=Format("{pos}. {item.full_name}"),
                on_click=on_select_shop_customer,
            ),
            id="all_shop_customers",
            width=2,
            height=10,
            hide_on_single_page=True,
            when=F["total"] > 0,
        ),
        getter=get_all_shop_customers,
        state=CustomerMenu.MAIN,
    ),
    Window(
        Format(
            "<b>Ім'я:</b> {full_name}\n"
            "<b>Телефон:</b> <code>{phone}</code>\n\n"
            "<b>Адреса:</b> {address}"
        ),
        Const("<b>Квартира:</b> ")
        + Case(
            texts={
                True: Format("{apartment_number}"),
                False: Const("частний будинок"),
            },
            selector=F["is_private_home"],
        ),
        Const("<b>Поверх:</b> ")
        + Case(
            texts={True: Format("{floor}"), False: Const("частний будинок")},
            selector=F["is_private_home"],
        ),
        Const("\n<b>Код домофону:</b> ")
        + Case(
            texts={True: Format("{intercom_code}"), False: Const("без коду")},
            selector=F["has_intercom_code"],
        ),
        get_back_btn(),
        getter=get_shop_customer,
        state=CustomerMenu.CUSTOMER_CARD,
    ),
)

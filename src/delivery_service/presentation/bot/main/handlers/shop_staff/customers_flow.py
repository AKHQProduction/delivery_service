from typing import Any

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.input import (
    ManagedTextInput,
    MessageInput,
    TextInput,
)
from aiogram_dialog.widgets.kbd import (
    Button,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Case, Const, Format
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.commands.add_new_customer import (
    AddNewCustomerRequest,
)
from delivery_service.application.commands.delete_customer import (
    DeleteCustomerRequest,
)
from delivery_service.application.common.errors import EntityAlreadyExistsError
from delivery_service.application.ports.location_finder import LocationFinder
from delivery_service.application.query.customer import GetAllCustomersRequest
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.domain.customer_registries.customer_registry import (
    AddressData,
    CoordinatesData,
)
from delivery_service.domain.customers.phone_number import PHONE_NUMBER_PATTERN
from delivery_service.domain.shared.user_id import UserID
from delivery_service.infrastructure.integration.geopy.errors import (
    LocationNotFoundError,
)
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

    dialog_manager.dialog_data["full_name"] = customer.full_name

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


async def get_customer_creation_data(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    data = dialog_manager.dialog_data

    full_name = data.get("new_customer_name")
    phone = data.get("new_customer_phone")
    city = data.get("city")
    street = data.get("street")
    house_number = data.get("house_number")
    floor = data.get("new_customer_floor", "частний будинок")
    apartment_number = data.get(
        "new_customer_apartment_number", "частний будинок"
    )
    intercom_code = data.get("new_customer_intercom_code", "без домофону")

    return {
        "full_name": full_name,
        "phone": phone,
        "address": f"{city}, {street} {house_number}",
        "floor": floor,
        "apartment_number": apartment_number,
        "intercom_code": intercom_code,
    }


async def on_input_customer_name(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["new_customer_name"] = value
    await manager.next()


async def on_input_customer_phone(
    msg: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    if not PHONE_NUMBER_PATTERN.match(value):
        await msg.answer("❌ Введіть корректний номер телефону")
        return

    manager.dialog_data["new_customer_phone"] = value
    await manager.next()


@inject
async def on_input_customer_location(
    msg: Message,
    __: MessageInput,
    manager: DialogManager,
    location_finder: FromDishka[LocationFinder],
) -> Message | None:
    wait_msg = await msg.answer("⏳ Перевіряємо адресу...")

    if msg.text:
        try:
            location = await location_finder.find_location(msg.text)
        except LocationNotFoundError:
            return await msg.answer(
                "Адресу не найдено.\n"
                "Введіть повторно або поділіться локацією 👇"
            )

        manager.dialog_data.update(
            {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "city": location.city,
                "street": location.street,
                "house_number": location.house_number,
            }
        )
        await wait_msg.delete()
        return await manager.next()
    raise ValueError()


async def on_input_customer_floor(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["new_customer_floor"] = value
    await manager.next()


async def on_input_customer_apartment_number(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["new_customer_apartment_number"] = value
    await manager.next()


async def on_input_customer_intercom_code(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["new_customer_intercom_code"] = value
    await manager.next()


async def on_select_shop_customer(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["customer_id"] = value
    await manager.switch_to(state=CustomerMenu.CUSTOMER_CARD)


@inject
async def on_accept_customer_delete(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    customer_id = get_customer_id(manager)

    await sender.send(DeleteCustomerRequest(customer_id=customer_id))

    if call.message:
        await call.message.answer("✅️ Клієнта успішно видалено")
    await manager.switch_to(state=CustomerMenu.MAIN, show_mode=ShowMode.SEND)


@inject
async def on_accept_customer_creation(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    data = manager.dialog_data

    full_name = data.get("new_customer_name")
    phone = data.get("new_customer_phone")
    city = data.get("city")
    street = data.get("street")
    house_number = data.get("house_number")
    floor = data.get("new_customer_floor")
    apartment_number = data.get("new_customer_apartment_number")
    intercom_code = data.get("new_customer_intercom_code")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if (
        not full_name
        or not phone
        or not house_number
        or not city
        or not street
        or not latitude
        or not longitude
    ):
        raise ValueError()

    try:
        response = await sender.send(
            AddNewCustomerRequest(
                full_name=full_name,
                phone_number=phone,
                address_data=AddressData(
                    city=city,
                    street=street,
                    house_number=house_number,
                    apartment_number=apartment_number,
                    floor=int(floor) if floor else None,
                    intercom_code=intercom_code,
                ),
                coordinates=CoordinatesData(
                    latitude=latitude, longitude=longitude
                ),
            )
        )
        manager.dialog_data["customer_id"] = str(response)
        if call.message:
            await call.message.answer("✅️ Клієнта додано")
        await manager.switch_to(
            state=CustomerMenu.CUSTOMER_CARD, show_mode=ShowMode.SEND
        )
    except EntityAlreadyExistsError:
        if call.message:
            await call.message.answer("❌ Клієнт з таким номером уже створено")
        await manager.switch_to(
            state=CustomerMenu.MAIN, show_mode=ShowMode.SEND
        )


switch_to_preview = SwitchTo(
    id="to_customer_preview",
    text=Const("Це частний будинок"),
    state=CustomerMenu.PREVIEW,
)

CUSTOMERS_DIALOG = Dialog(
    Window(
        Const("<b>Меню клієнтів</b>"),
        SwitchTo(
            text=Const("➕ Додать клієнта"),
            state=CustomerMenu.NEW_CUSTOMER_NAME,
            id="add_new_customer",
        ),
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
        Row(
            SwitchTo(
                id="edit_customer",
                text=Const("✏️ Редактировать"),
                state=CustomerMenu.EDIT_MENU,
            ),
            SwitchTo(
                id="delete_customer",
                text=Const("🗑 Видалить"),
                state=CustomerMenu.DELETE_CONFIRMATION,
            ),
        ),
        get_back_btn(),
        getter=get_shop_customer,
        state=CustomerMenu.CUSTOMER_CARD,
    ),
    Window(
        Format(
            "Підтвердіть видалення {dialog_data[full_name]} з бази клієнтів"
        ),
        Button(
            text=Const("✅ Підтвердити"),
            id="accept_customer_delete",
            on_click=on_accept_customer_delete,
        ),
        get_back_btn(
            btn_text="❌ Відмінити", state=CustomerMenu.CUSTOMER_CARD
        ),
        state=CustomerMenu.DELETE_CONFIRMATION,
    ),
    Window(
        Const("1️⃣ Вкажіть ім'я клієнта"),
        TextInput(id="input_customer_name", on_success=on_input_customer_name),
        get_back_btn(state=CustomerMenu.MAIN),
        state=CustomerMenu.NEW_CUSTOMER_NAME,
    ),
    Window(
        Const("2️⃣ Вкажіть телефон клієнта"),
        Const("<i>В форматі +380</i>"),
        TextInput(
            id="input_customer_phone", on_success=on_input_customer_phone
        ),
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_NAME),
        state=CustomerMenu.NEW_CUSTOMER_PHONE,
    ),
    Window(
        Const("3️⃣ Вкажіть адресу клієнта"),
        Const(
            "<i>Якщо виникли складноші - перевірте вашу адресу"
            " на карті: https://www.openstreetmap.org</i>"
        ),
        MessageInput(filter=F.text, func=on_input_customer_location),
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_PHONE),
        state=CustomerMenu.NEW_CUSTOMER_ADDRESS,
    ),
    Window(
        Const("4️⃣ Вкажіть поверх для доставки"),
        TextInput(
            id="input_customer_floor", on_success=on_input_customer_floor
        ),
        switch_to_preview,
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_ADDRESS),
        state=CustomerMenu.NEW_CUSTOMER_FLOOR,
    ),
    Window(
        Const("5️⃣ Вкажіть номер квартири"),
        TextInput(
            id="input_customer_apartment_number",
            on_success=on_input_customer_apartment_number,
        ),
        switch_to_preview,
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_FLOOR),
        state=CustomerMenu.NEW_CUSTOMER_APARTMENT_NUMBER,
    ),
    Window(
        Const("6️⃣ Вкажіть код домофону"),
        TextInput(
            id="input_customer_apartment_number",
            on_success=on_input_customer_intercom_code,
        ),
        SwitchTo(
            id="to_customer_preview",
            text=Const("Відсутній"),
            state=CustomerMenu.PREVIEW,
        ),
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_FLOOR),
        state=CustomerMenu.NEW_CUSTOMER_INTERCOM_CODE,
    ),
    Window(
        Const("<b>Перевірте данні нового клієнта</b>\n"),
        Format(
            "<b>Ім'я:</b> {full_name}\n"
            "<b>Телефон:</b> <code>{phone}</code>\n\n"
            "<b>Адреса:</b> {address}\n"
            "<b>Квартира:</b> {apartment_number}\n"
            "<b>Поверх:</b> {floor}\n\n"
            "<b>Код домофону:</b> {intercom_code}\n"
        ),
        Const("<b>Підтвердіть створення клієнта👇</b>"),
        Button(
            text=Const("✅ Підтвердити"),
            id="accept_customer_creation",
            on_click=on_accept_customer_creation,
        ),
        get_back_btn(btn_text="❌ Відмінити", state=CustomerMenu.MAIN),
        getter=get_customer_creation_data,
        state=CustomerMenu.PREVIEW,
    ),
)

import logging
from typing import Any

from aiogram import F, Router
from aiogram.fsm.state import State
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
from aiogram_dialog.widgets.text import Const, Format, Multi
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.commands.add_new_customer import (
    AddNewCustomerRequest,
)
from delivery_service.application.commands.delete_customer import (
    DeleteCustomerRequest,
)
from delivery_service.application.commands.edit_customer import (
    EditCustomerAddressRequest,
    EditCustomerNameRequest,
    EditCustomerPrimaryPhoneRequest,
)
from delivery_service.application.common.errors import EntityAlreadyExistsError
from delivery_service.application.ports.location_finder import LocationFinder
from delivery_service.application.query.customer import GetAllCustomersRequest
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.domain.customers.phone_number import PHONE_NUMBER_PATTERN
from delivery_service.domain.shared.dto import AddressData, CoordinatesData
from delivery_service.infrastructure.integration.geopy.errors import (
    LocationNotFoundError,
)
from delivery_service.infrastructure.integration.telegram.const import (
    CUSTOMERS_BTN,
)
from delivery_service.presentation.bot.widgets.kbd import get_back_btn

from .getters import get_customer_addresses, get_customer_id
from .states import CustomerMenu

CUSTOMERS_ROUTER = Router()


@CUSTOMERS_ROUTER.message(F.text == CUSTOMERS_BTN)
async def launch_customer_dialog(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=CustomerMenu.MAIN, mode=StartMode.RESET_STACK
    )


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
        "addresses": customer.delivery_addresses,
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


@inject
async def on_input_new_customer_name(
    _: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
    sender: FromDishka[Sender],
) -> None:
    customer_id = get_customer_id(manager)
    await sender.send(
        EditCustomerNameRequest(customer_id=customer_id, new_name=value)
    )

    await manager.switch_to(state=CustomerMenu.EDIT_MENU)


async def on_input_customer_phone(
    msg: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    if not PHONE_NUMBER_PATTERN.match(value):
        await msg.answer("❌ Введіть корректний номер телефону")
        return

    manager.dialog_data["new_customer_phone"] = value
    await manager.next()


@inject
async def on_input_new_customer_phone(
    msg: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
    sender: FromDishka[Sender],
) -> None:
    if not PHONE_NUMBER_PATTERN.match(value):
        await msg.answer("❌ Введіть корректний номер телефону")
        return

    customer_id = get_customer_id(manager)
    await sender.send(
        EditCustomerPrimaryPhoneRequest(
            customer_id=customer_id, new_phone=value
        )
    )
    await manager.switch_to(state=CustomerMenu.EDIT_MENU)


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


@inject
async def on_input_new_customer_address(
    _: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
    sender: FromDishka[Sender],
) -> None:
    manager.dialog_data["new_customer_intercom_code"] = value
    await edit_customer_address(manager, sender)


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
        manager.dialog_data["new_customer_apartment_number"] = None
        manager.dialog_data["new_customer_floor"] = None
        manager.dialog_data["new_customer_intercom_code"] = None

        logging.info(manager.dialog_data)
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


@inject
async def on_edit_customer_address(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    await edit_customer_address(manager, sender)


async def edit_customer_address(
    manager: DialogManager, sender: Sender
) -> None:
    data = manager.dialog_data
    customer_id = get_customer_id(manager)

    city = data.get("city")
    street = data.get("street")
    house_number = data.get("house_number")
    floor = data.get("new_customer_floor")
    apartment_number = data.get("new_customer_apartment_number")
    intercom_code = data.get("new_customer_intercom_code")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if (
        not house_number
        or not city
        or not street
        or not latitude
        or not longitude
    ):
        raise ValueError()

    await sender.send(
        EditCustomerAddressRequest(
            customer_id=customer_id,
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

    await manager.switch_to(state=CustomerMenu.EDIT_MENU)


def get_switch_to_preview(state: State) -> SwitchTo:
    return SwitchTo(
        id="to_customer_preview",
        text=Const("Це частний будинок"),
        state=state,
    )


CUSTOMER_CARD = Multi(
    Format(
        "<b>Ім'я:</b> {full_name}\n"
        "<b>Телефон:</b> <code>{phone}</code>\n\n"
        "<b>Адреса:</b> {addresses[0].city}, {addresses[0].street} "
        "{addresses[0].house_number}"
    )
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
        CUSTOMER_CARD,
        Row(
            SwitchTo(
                id="edit_customer",
                text=Const("✏️ Редагувати"),
                state=CustomerMenu.EDIT_MENU,
            ),
            SwitchTo(
                id="delete_customer",
                text=Const("🗑 Видалить"),
                state=CustomerMenu.DELETE_CONFIRMATION,
            ),
        ),
        get_back_btn(),
        getter=[get_shop_customer, get_customer_addresses],
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
        get_switch_to_preview(CustomerMenu.PREVIEW),
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_ADDRESS),
        state=CustomerMenu.NEW_CUSTOMER_FLOOR,
    ),
    Window(
        Const("5️⃣ Вкажіть номер квартири"),
        TextInput(
            id="input_customer_apartment_number",
            on_success=on_input_customer_apartment_number,
        ),
        get_switch_to_preview(CustomerMenu.PREVIEW),
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
    Window(
        Const("<b>Меню редагування клієнта</b>\n"),
        CUSTOMER_CARD,
        Row(
            SwitchTo(
                id="edit_customer_name",
                text=Const("Редагувати ім'я"),
                state=CustomerMenu.EDIT_CUSTOMER_NAME,
            ),
            SwitchTo(
                id="edit_customer_primary_phone",
                text=Const("Редагувати контактний телефон"),
                state=CustomerMenu.EDIT_CUSTOMER_PHONE,
            ),
        ),
        SwitchTo(
            id="edit_customer_delivery_address",
            text=Const("Редагувати адресу доставки"),
            state=CustomerMenu.EDIT_CUSTOMER_ADDRESS,
        ),
        get_back_btn(state=CustomerMenu.CUSTOMER_CARD),
        getter=[get_shop_customer, get_customer_addresses],
        state=CustomerMenu.EDIT_MENU,
    ),
    Window(
        Const("Вкажіть нове ім'я клієнта"),
        TextInput(
            id="input_new_customer_name", on_success=on_input_new_customer_name
        ),
        get_back_btn(state=CustomerMenu.EDIT_MENU),
        state=CustomerMenu.EDIT_CUSTOMER_NAME,
    ),
    Window(
        Const("Вкажіть новий контактний номер телефона клієнта"),
        Const("<i>В форматі +380</i>"),
        TextInput(
            id="input_new_customer_phone",
            on_success=on_input_new_customer_phone,
        ),
        get_back_btn(state=CustomerMenu.EDIT_MENU),
        state=CustomerMenu.EDIT_CUSTOMER_PHONE,
    ),
    Window(
        Const("Вкажіть нову адресу доставки клієнта"),
        Const(
            "<i>Якщо виникли складноші - перевірте вашу адресу"
            " на карті: https://www.openstreetmap.org</i>"
        ),
        MessageInput(filter=F.text, func=on_input_customer_location),
        get_back_btn(state=CustomerMenu.EDIT_MENU),
        state=CustomerMenu.EDIT_CUSTOMER_ADDRESS,
    ),
    Window(
        Const("Вкажіть поверх для доставки"),
        TextInput(
            id="input_customer_floor", on_success=on_input_customer_floor
        ),
        get_switch_to_preview(CustomerMenu.EDIT_CUSTOMER_INTERCOM_CODE),
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_ADDRESS),
        state=CustomerMenu.EDIT_CUSTOMER_FLOOR,
    ),
    Window(
        Const("Вкажіть номер квартири"),
        TextInput(
            id="input_customer_apartment_number",
            on_success=on_input_customer_apartment_number,
        ),
        get_switch_to_preview(CustomerMenu.EDIT_CUSTOMER_INTERCOM_CODE),
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_FLOOR),
        state=CustomerMenu.EDIT_CUSTOMER_APARTMENT_NUMBER,
    ),
    Window(
        Const("Вкажіть код домофону"),
        TextInput(
            id="input_customer_apartment_number",
            on_success=on_input_new_customer_address,
        ),
        Button(
            id="to_customer_preview",
            text=Const("Відсутній"),
            on_click=on_edit_customer_address,
        ),
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_FLOOR),
        state=CustomerMenu.EDIT_CUSTOMER_INTERCOM_CODE,
    ),
)

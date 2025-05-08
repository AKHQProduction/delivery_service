from typing import Any
from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (
    Data,
    Dialog,
    DialogManager,
    ShowMode,
    StartMode,
    Window,
)
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
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja, Multi
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from magic_filter import MagicFilter

from delivery_service.application.commands.add_customer_address import (
    AddAddressToCustomerRequest,
)
from delivery_service.application.commands.add_new_customer import (
    AddNewCustomerRequest,
)
from delivery_service.application.commands.delete_customer import (
    DeleteCustomerRequest,
)
from delivery_service.application.commands.delete_customer_address import (
    DeleteCustomerAddressRequest,
)
from delivery_service.application.commands.edit_customer import (
    EditCustomerNameRequest,
    EditCustomerPrimaryPhoneRequest,
)
from delivery_service.application.common.errors import EntityAlreadyExistsError
from delivery_service.application.ports.location_finder import LocationFinder
from delivery_service.application.query.customer import GetAllCustomersRequest
from delivery_service.application.query.ports.address_gateway import (
    AddressGateway,
)
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.domain.customers.phone_number import PHONE_NUMBER_PATTERN
from delivery_service.domain.customers.phone_number_id import PhoneNumberID
from delivery_service.domain.shared.dto import AddressData, CoordinatesData
from delivery_service.infrastructure.integration.geopy.errors import (
    LocationNotFoundError,
)
from delivery_service.infrastructure.integration.telegram.const import (
    CUSTOMERS_BTN,
)
from delivery_service.presentation.bot.widgets.kbd import get_back_btn

from .getters import get_address_id, get_customer_id
from .states import AddressSG, CustomerMenu

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

    dialog_manager.dialog_data["name"] = customer.name

    return {
        "name": customer.name,
        "addresses": customer.addresses,
        "phone_numbers": customer.phone_numbers,
    }


async def get_customer_creation_data(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    data = dialog_manager.dialog_data

    name = data.get("new_customer_name")
    phone = data.get("new_customer_phone")
    city = data.get("city")
    street = data.get("street")
    house_number = data.get("house_number")
    floor = data.get("floor", "приватний будинок")
    apartment_number = data.get("apartment_number", "приватний будинок")
    intercom_code = data.get("intercom_code", "без домофону")

    return {
        "name": name,
        "phone": phone,
        "address": f"{city}, {street} {house_number}",
        "floor": floor,
        "apartment_number": apartment_number,
        "intercom_code": intercom_code,
    }


@inject
async def get_address(
    dialog_manager: DialogManager,
    reader: FromDishka[AddressGateway],
    **_kwargs,
) -> dict[str, Any]:
    address_id = get_address_id(dialog_manager)

    address = await reader.read_with_id(address_id)
    if not address:
        raise ValueError()

    return {
        "full_address": address.full_address,
        "apartment_number": address.apartment_number
        if address.apartment_number
        else "приватний будинок",
        "floor": address.floor if address.floor else "приватний будинок",
        "intercom_code": address.intercom_code
        if address.intercom_code
        else "без коду",
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
    await manager.start(state=AddressSG.FULL_ADDRESS)


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
            customer_id=customer_id,
            new_primary_phone=PhoneNumberID(UUID(value)),
        )
    )
    await manager.switch_to(state=CustomerMenu.EDIT_MENU)


async def on_select_shop_customer(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["customer_id"] = value
    await manager.switch_to(state=CustomerMenu.CUSTOMER_CARD)


async def on_select_address(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["address_id"] = value
    await manager.switch_to(state=CustomerMenu.ADDRESS_CARD)


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
async def on_accept_address_delete(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    address_id = get_address_id(manager)
    customer_id = get_customer_id(manager)

    await sender.send(
        DeleteCustomerAddressRequest(
            customer_id=customer_id, address_id=address_id
        )
    )

    if call.message:
        await call.message.answer("✅️ Адресу клієнта успішно видалено")
    await manager.switch_to(
        state=CustomerMenu.CUSTOMER_CARD, show_mode=ShowMode.SEND
    )


@inject
async def on_accept_customer_creation(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    data = manager.dialog_data

    name = data.get("new_customer_name")
    phone = data.get("new_customer_phone")
    city = data.get("city")
    street = data.get("street")
    house_number = data.get("house_number")
    floor = data.get("floor")
    apartment_number = data.get("apartment_number")
    intercom_code = data.get("intercom_code")
    latitude = data.get("latitude")
    longitude = data.get("longitude")

    if (
        not name
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
                name=name,
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
        manager.dialog_data.clear()
        manager.dialog_data["customer_id"] = str(response)

        if call.message:
            await call.message.answer("✅️ Клієнта додано")
        await manager.switch_to(
            state=CustomerMenu.CUSTOMER_CARD, show_mode=ShowMode.SEND
        )
    except EntityAlreadyExistsError:
        if call.message:
            await call.message.answer(
                "❌ Клієнт з таким номером або адресою уже створено"
            )
        await manager.switch_to(
            state=CustomerMenu.MAIN, show_mode=ShowMode.SEND
        )


async def on_result_input_new_customer_address(
    _: Data,
    result: dict[str, Any],
    manager: DialogManager,
):
    if result:
        manager.dialog_data.update(result)

    await manager.switch_to(state=CustomerMenu.PREVIEW)


@inject
async def on_result_add_new_customer_address(
    _: Data,
    result: dict[str, Any],
    manager: DialogManager,
    sender: FromDishka[Sender],
):
    customer_id = get_customer_id(manager)
    if result:
        await sender.send(
            AddAddressToCustomerRequest(
                customer_id=customer_id,
                address_data=AddressData(
                    city=result["city"],
                    street=result["street"],
                    house_number=result["house_number"],
                    apartment_number=result.get("apartment_number"),
                    floor=result.get("floor"),
                    intercom_code=result.get("intercom_code"),
                ),
                coordinates=CoordinatesData(
                    latitude=result["latitude"], longitude=result["longitude"]
                ),
            )
        )


CUSTOMER_CARD = Multi(
    Format("<b>Ім'я:</b> {name}\n"),
    Jinja(
        "<b>Адреси клієнта:</b>"
        "<blockquote expandable>"
        "{% if addresses %}"
        "{% for address in addresses %}"
        "- <i>{{address.city}}, {{address.street}} "
        "{{address.house_number}}</i>\n"
        "{% endfor %}"
        "{% else %}"
        "Адреси відсутні"
        "{% endif %}"
        "</blockquote>"
    ),
    Jinja(
        "<b>Телефонні номера клієнта:</b>"
        "<blockquote expandable>"
        "{% if phone_numbers %}"
        "{% for phone in phone_numbers %}"
        "- <i>{{phone.number}}</i>\n"
        "{% endfor %}"
        "{% else %}"
        "Телефони відсутні"
        "{% endif %}"
        "</blockquote>"
    ),
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
                text=Format("{pos}. {item.name}"),
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
        getter=get_shop_customer,
        state=CustomerMenu.CUSTOMER_CARD,
    ),
    Window(
        Format("Підтвердіть видалення {dialog_data[name]} з бази клієнтів"),
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
        Const("Вкажіть ім'я клієнта"),
        TextInput(id="input_customer_name", on_success=on_input_customer_name),
        get_back_btn(state=CustomerMenu.MAIN),
        state=CustomerMenu.NEW_CUSTOMER_NAME,
    ),
    Window(
        Const("Вкажіть телефон клієнта"),
        Const("<i>В форматі +380</i>"),
        TextInput(
            id="input_customer_phone", on_success=on_input_customer_phone
        ),
        get_back_btn(state=CustomerMenu.NEW_CUSTOMER_NAME),
        state=CustomerMenu.NEW_CUSTOMER_PHONE,
        on_process_result=on_result_input_new_customer_address,
    ),
    Window(
        Const("<b>Перевірте данні нового клієнта</b>\n"),
        Format(
            "<b>Ім'я:</b> {name}\n"
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
        SwitchTo(
            id="edit_customer_name",
            text=Const("Редагувати ім'я"),
            state=CustomerMenu.EDIT_CUSTOMER_NAME,
        ),
        Row(
            SwitchTo(
                id="edit_customer_primary_phone",
                text=Const("Редагувати номери клієнта"),
                state=CustomerMenu.EDIT_CUSTOMER_PHONE,
            ),
            SwitchTo(
                id="edit_customer_delivery_address",
                text=Const("Редагувати адреси клієнта"),
                state=CustomerMenu.ADDRESSES_MENU,
            ),
        ),
        get_back_btn(state=CustomerMenu.CUSTOMER_CARD),
        getter=get_shop_customer,
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
        Format("Адреси {dialog_data[name]}"),
        Start(
            text=Const("➕ Додать адресу"),
            state=AddressSG.FULL_ADDRESS,
            id="add_new_address",
        ),
        ScrollingGroup(
            Select(
                id="address_item",
                items="addresses",
                item_id_getter=lambda item: item.address_id,
                text=Format(
                    "{pos}. {item.city}, {item.street} {item.house_number}"
                ),
                on_click=on_select_address,
            ),
            id="all_customer_addresses",
            width=2,
            height=10,
            hide_on_single_page=True,
            when=MagicFilter.len(F["addresses"]) > 0,
        ),
        get_back_btn(state=CustomerMenu.EDIT_MENU),
        getter=get_shop_customer,
        state=CustomerMenu.ADDRESSES_MENU,
        on_process_result=on_result_add_new_customer_address,
    ),
    Window(
        Format(
            "<b>Адреса:</b> {full_address}\n"
            "<b>Квартира:</b> {apartment_number}\n"
            "<b>Поверх:</b> {floor}\n"
            "<b>Код домофону:</b> {intercom_code}"
        ),
        SwitchTo(
            id="delete_address",
            text=Const("🗑 Видалить"),
            state=CustomerMenu.DELETE_ADDRESS,
        ),
        get_back_btn(state=CustomerMenu.ADDRESSES_MENU),
        getter=get_address,
        state=CustomerMenu.ADDRESS_CARD,
    ),
    Window(
        Format(
            "Видалить адресу {full_address} у користувача {dialog_data[name]}?"
        ),
        Button(
            text=Const("✅ Підтвердити"),
            id="accept_address_delete",
            on_click=on_accept_address_delete,
        ),
        get_back_btn(btn_text="❌ Відмінити", state=CustomerMenu.ADDRESS_CARD),
        getter=get_address,
        state=CustomerMenu.DELETE_ADDRESS,
    ),
)


async def on_finish_address_dialog(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
) -> None:
    await manager.done(manager.dialog_data)


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


async def on_input_customer_apartment_number(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["apartment_number"] = value
    await manager.next()


async def on_input_customer_floor(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["floor"] = value
    await manager.next()


async def on_input_customer_intercom_code(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["intercom_code"] = value
    await manager.done(result=manager.dialog_data)


ADDRESS_DATA_ENTRY_DIALOG = Dialog(
    Window(
        Const("Вкажіть адресу клієнта"),
        Const(
            "<i>Якщо виникли складноші - перевірте вашу адресу"
            " на карті: https://www.openstreetmap.org</i>"
        ),
        MessageInput(filter=F.text, func=on_input_customer_location),
        get_back_btn(state=CustomerMenu.MAIN, back_to_prev_dialog=True),
        state=AddressSG.FULL_ADDRESS,
    ),
    Window(
        Const("Вкажіть номер квартири"),
        TextInput(
            id="input_customer_apartment_number",
            on_success=on_input_customer_apartment_number,
        ),
        Button(
            text=Const("Це приватний будинок"),
            id="private_house",
            on_click=on_finish_address_dialog,
        ),
        get_back_btn(state=AddressSG.FULL_ADDRESS),
        state=AddressSG.APARTMENT_NUMBER,
    ),
    Window(
        Const("Вкажіть поверх для доставки"),
        TextInput(
            id="input_customer_floor", on_success=on_input_customer_floor
        ),
        get_back_btn(state=AddressSG.APARTMENT_NUMBER),
        state=AddressSG.FLOOR,
    ),
    Window(
        Const("Вкажіть код домофону"),
        TextInput(
            id="input_customer_apartment_number",
            on_success=on_input_customer_intercom_code,
        ),
        Button(
            id="to_customer_preview",
            text=Const("Відсутній"),
            on_click=on_finish_address_dialog,
        ),
        get_back_btn(state=AddressSG.FLOOR),
        state=AddressSG.INTERCOM_CODE,
    ),
)

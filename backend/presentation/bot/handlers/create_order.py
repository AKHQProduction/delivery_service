from datetime import date
from typing import Any

from dishka import FromDishka
from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import (
    Dialog,
    Window,
    DialogManager,
    StartMode,
    ChatEvent
)
from aiogram_dialog.widgets.input import (
    MessageInput,
    TextInput,
    ManagedTextInput
)
from aiogram_dialog.widgets.kbd import (
    ManagedCalendar,
    Button,
    Counter,
    Next, Cancel
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka.integrations.aiogram_dialog import inject

from domain.value_objects.phone_number import PhoneNumber
from infrastructure.geopy.errors import AddressIsNotExists
from infrastructure.geopy.geopy_processor import GeoProcessor
from presentation.bot import states
from presentation.bot.widgets import CustomCalendar

router = Router()


@router.message(F.text == "🛒 Створити замовлення")
async def init_create_order_dialog(
        _: Message,
        dialog_manager: DialogManager,
):
    await dialog_manager.start(
        state=states.CreateOrder.WATER_TYPE,
        mode=StartMode.RESET_STACK
    )


async def on_select_water_type(
        _: CallbackQuery,
        widget: Button,
        manager: DialogManager
):
    manager.dialog_data["water_type"] = widget.widget_id

    await manager.next()


async def on_quantity_confirmation(
        call: CallbackQuery,
        _: Button,
        manager: DialogManager,
):
    quantity: int = manager.find("water_quantity_counter").get_value()

    if quantity == 0:
        return await call.answer("Кількість повинна бути більша 0")

    manager.dialog_data["quantity"] = quantity

    await manager.next()


async def on_select_delivery_date(
        call: ChatEvent,
        _: ManagedCalendar,
        manager: DialogManager,
        selected_date: date
):
    current_date: date = date.today()

    if current_date > selected_date:
        return await call.answer("Дата вибрана некорректно")

    manager.dialog_data["delivery_date"] = selected_date

    await manager.next()


async def on_select_delivery_time(
        _: CallbackQuery,
        widget: Button,
        manager: DialogManager):
    manager.dialog_data["delivery_time"] = widget.widget_id

    await manager.next()


@inject
async def on_input_user_address(
        msg: Message,
        _: MessageInput,
        manager: DialogManager,
        geolocator: FromDishka[GeoProcessor]

):
    try:
        latitude, longitude = await geolocator.get_coordinates(msg.text)

        manager.dialog_data["latitude"] = latitude
        manager.dialog_data["longitude"] = longitude
        manager.dialog_data["address"] = msg.text

        await manager.next()
    except AddressIsNotExists:
        await msg.answer(
            "😥 На жаль, ми не змогли Вашої адреси"
        )


async def on_error_input_phone_number(
        msg: Message,
        _: Any,
        __: DialogManager,
        ___: ValueError
):
    await msg.answer(
        "Ви ввели некоректний номер телефону"
    )


async def get_dialog_data(
        dialog_manager: DialogManager,
        **_kwargs
) -> dict[str, Any]:
    data: dict[str, Any] = dialog_manager.dialog_data

    water_type: str = (
        "звичайна" if data["water_type"] == "default_water" else "магнезія"
    )

    delivery_time: str = (
        "перша половина дня" if data["delivery_time"] == "morning"
        else "друга половина дня"
    )

    phone_input_widget: ManagedTextInput = dialog_manager.find("phone_input")
    phone_data: PhoneNumber = phone_input_widget.get_value()

    data["water_type"] = water_type
    data["delivery_time"] = delivery_time
    data["phone"] = phone_data.to_raw()

    delivery_date: date = data["delivery_date"].strftime("%d.%m.%Y")

    data["delivery_date"] = delivery_date

    return data


async def on_successful_confirm_order(
        call: CallbackQuery,
        _: Button,
        manager: DialogManager
):
    await call.message.answer("🎉 Ваше замовлення прийняте")

    await manager.done()


async def on_reject_order(
        call: CallbackQuery,
        _: Button,
        manager: DialogManager
):
    await call.message.answer("👀 Будемо очікувати від Вас замовлення")

    await manager.done()


create_order_dialog = Dialog(
    Window(
        Const("1️⃣ Виберіть воду для замовлення"),
        Button(
            Const("Звичайна"),
            id="default_water",
            on_click=on_select_water_type
        ),
        Button(
            Const("Магнезія"),
            id="magnesia_water",
            on_click=on_select_water_type
        ),
        state=states.CreateOrder.WATER_TYPE
    ),
    Window(
        Const("2️⃣ Вкажіть кількість бутлів"),
        Counter(
            id="water_quantity_counter",
        ),
        Button(
            Const("✅ Підтвердити"),
            id="quantity_confirmation",
            on_click=on_quantity_confirmation
        ),
        state=states.CreateOrder.QUANTITY
    ),
    Window(
        Const("3️⃣ Вкажіть дату доставки"),
        CustomCalendar(
            id="delivery_date",
            on_click=on_select_delivery_date
        ),
        state=states.CreateOrder.DELIVERY_DATE,
    ),
    Window(
        Const("4️⃣ Коли саме Ви хочете отримати замовлення"),
        Button(
            Const("Перша половина дня"),
            id="morning",
            on_click=on_select_delivery_time
        ),
        Button(
            Const("Друга половина дня"),
            id="afternoon",
            on_click=on_select_delivery_time
        ),
        state=states.CreateOrder.DELIVERY_TIME
    ),
    Window(
        Const("5️⃣ Вкажіть Вашу адресу👇"),
        MessageInput(
            on_input_user_address,
            content_types=[ContentType.TEXT]
        ),
        state=states.CreateOrder.ADDRESS
    ),
    Window(
        Multi(
            Const("6️⃣ Введіть ваш номер телефону👇"),
            Const("<i>В форматі +380</i>"),
            sep="\n\n"
        ),
        TextInput(
            id="phone_input",
            type_factory=lambda x: PhoneNumber(value=x),
            on_success=Next(),
            on_error=on_error_input_phone_number,
        ),
        state=states.CreateOrder.PHONE
    ),
    Window(
        Const("<b>⚠️Перевірте Ваше замовлення</b> \n"),

        Multi(
            Format("<b>💧 Вода:</b> {water_type}"),
            Format("<b>📦 Кількість:</b> {quantity}"),
            Format("<b>🗓 Дата доставки:</b> {delivery_date}"),
            Format("<b>⏰ Час доставки:</b> {delivery_time}"),
            Format("<b>🏠 Адреса:</b> {address}"),
            Format("<b>📞 Номер телефону</b> {phone}"),
            sep="\n"
        ),
        Button(
            Const("✅ Підтвердити"),
            id="confirm_order",
            on_click=on_successful_confirm_order
        ),
        Cancel(
            Const("❌ Відмовитись"),
            id="reject_order",
            on_click=on_reject_order
        ),
        state=states.CreateOrder.CONFIRMATION,
        getter=get_dialog_data
    )
)

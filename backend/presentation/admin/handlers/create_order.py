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
    TextInput
)
from aiogram_dialog.widgets.kbd import (
    ManagedCalendar,
    Button,
    Counter,
    Next, Cancel
)
from aiogram_dialog.widgets.text import Const, Format, Multi, Case, Jinja
from dishka.integrations.aiogram_dialog import inject

from entities.user.value_objects.phone_number import PhoneNumber
from infrastructure.geopy.errors import (
    AddressIsNotExists,
    GeolocatorBadGateway
)
from infrastructure.geopy.geopy_processor import GeoProcessor
from presentation.admin import states
from presentation.admin.helpers import (
    is_address_specific_enough, is_contains_emoji,
)
from presentation.admin.dialogs.widgets.common.calendar import CustomCalendar

router = Router()

ORDER_CREATED_KEY = "order_created"


@router.message(F.text == "🛒 Створити замовлення")
async def init_create_order_dialog(
        _: Message,
        dialog_manager: DialogManager,
):
    await dialog_manager.start(
        state=states.CreateOrder.WATER_TYPE,
        mode=StartMode.RESET_STACK,
        data={
            ORDER_CREATED_KEY: False
        }
    )


DEFAULT_WATER_TYPE_TEXT = "Звичайна"
MAGNESIA_WATER_TYPE_TEXT = "Магнезія"

MORNING_TEXT = "Перша половина дня"
AFTERNOON_TEXT = "Друга половина дня"


async def on_start_create_order_dialog(
        data: dict[str, Any],
        manager: DialogManager
) -> None:
    manager.dialog_data[ORDER_CREATED_KEY] = data[ORDER_CREATED_KEY]
    manager.dialog_data["is_private_house"] = False


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
    # TODO: Make from this VO, and use TextInput

    current_date: date = date.today()

    if current_date > selected_date:
        return await call.answer("Дата вибрана некорректно")

    if not (
            selected_date.month == current_date.month
            and
            selected_date.year == current_date.year
    ):
        return await call.answer(
            f"Замовлення приймаются в рамках поточного місяця"
        )

    manager.dialog_data["delivery_date"] = selected_date

    await manager.next()


async def on_select_delivery_time(
        _: CallbackQuery,
        widget: Button,
        manager: DialogManager
):
    manager.dialog_data["delivery_time"] = widget.widget_id

    await manager.next()


@inject
async def on_input_user_address(
        msg: Message,
        _: MessageInput,
        manager: DialogManager,
        geolocator: FromDishka[GeoProcessor]

):
    waiting_msg = await msg.answer("⏳ Шукаємо вашу адресу...")

    if (
            not is_address_specific_enough(msg.text)
            and
            is_contains_emoji(msg.text)
    ):
        await waiting_msg.delete()

        return await msg.answer(
            "🙅‍♀️ Будь ласка, введіть корректну адресу"
        )

    try:
        latitude, longitude = await geolocator.get_coordinates(msg.text)

        manager.dialog_data["latitude"] = latitude
        manager.dialog_data["longitude"] = longitude
        manager.dialog_data["address"] = msg.text

        await manager.next()
    except AddressIsNotExists:
        await msg.answer(
            "😥 На жаль, ми не змогли знайти Вашої адреси"
        )
    except GeolocatorBadGateway:
        await msg.answer(
            "🥺 На жаль, сталась помилка. Повторіть Ваш запит пізніше"
        )
    finally:
        await waiting_msg.delete()


def check_apartment_number(value: str):
    if not value.isdigit() or int(value) < 1:
        raise ValueError
    return value


async def on_select_private_house(
        _: CallbackQuery,
        __: Button,
        manager: DialogManager
):
    manager.dialog_data["is_private_house"] = True

    await manager.next()


async def get_create_order_dialog_data(
        dialog_manager: DialogManager,
        **_kwargs
) -> dict[str, Any]:
    phone_data: PhoneNumber = dialog_manager.find("phone_input").get_value()
    dialog_manager.dialog_data["phone"] = phone_data.to_raw()

    dialog_manager.dialog_data["apartment"] = (
        dialog_manager.find("apartment_input").get_value()
    )

    return dialog_manager.dialog_data


async def on_successful_confirm_order(
        call: CallbackQuery,
        _: Button,
        manager: DialogManager
):
    await call.message.answer("🎉 Ваше замовлення прийняте")

    manager.dialog_data[ORDER_CREATED_KEY] = True

    await manager.done()


async def on_reject_order(
        call: CallbackQuery,
        _: Button,
        manager: DialogManager
):
    await call.message.answer("👀 Будемо очікувати від Вас замовлення")

    await manager.done()


async def on_close_create_order_dialog(
        _data: dict[str, Any],
        manager: DialogManager
) -> None:
    is_order_created: bool = manager.dialog_data[ORDER_CREATED_KEY]

    if is_order_created:
        # TODO: Add order to db
        print("Successfully")
    manager.dialog_data.clear()


create_order_dialog = Dialog(
    Window(
        Const("1️⃣ <b>Виберіть воду для замовлення</b>"),
        Button(
            Const(DEFAULT_WATER_TYPE_TEXT),
            id="default_water",
            on_click=on_select_water_type
        ),
        Button(
            Const(MAGNESIA_WATER_TYPE_TEXT),
            id="magnesia_water",
            on_click=on_select_water_type
        ),
        state=states.CreateOrder.WATER_TYPE
    ),
    Window(
        Const("2️⃣ <b>Вкажіть кількість бутлів</b>"),
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
        Const("3️⃣ <b>Вкажіть дату доставки</b>"),
        CustomCalendar(
            id="delivery_date",
            on_click=on_select_delivery_date
        ),
        state=states.CreateOrder.DELIVERY_DATE,
    ),
    Window(
        Const("4️⃣ <b>Коли саме Ви хочете отримати замовлення</b>"),
        Button(
            Const(MORNING_TEXT),
            id="morning",
            on_click=on_select_delivery_time
        ),
        Button(
            Const(AFTERNOON_TEXT),
            id="afternoon",
            on_click=on_select_delivery_time
        ),
        state=states.CreateOrder.DELIVERY_TIME
    ),
    Window(
        Const(
            "5️⃣ <b>Вкажіть Вашу адресу👇</b>\n"
            "<i>Наприклад: бульвар Шевченка 42</i>"
        ),
        MessageInput(
            on_input_user_address,
            content_types=[ContentType.TEXT]
        ),
        state=states.CreateOrder.ADDRESS
    ),
    Window(
        Const("6️⃣ <b>Вкажіть номер Вашої квартири👇</b>"),
        TextInput(
            id="apartment_input",
            type_factory=check_apartment_number,
            on_success=Next()
        ),
        Button(
            id="is_private_house",
            text=Const("Це приватний будинок"),
            on_click=on_select_private_house
        ),
        state=states.CreateOrder.APARTMENT
    ),
    Window(
        Multi(
            Const("7️⃣ <b>Введіть ваш номер телефону👇</b>"),
            Const("<i>В форматі +380</i>"),
            sep="\n\n"
        ),
        TextInput(
            id="phone_input",
            type_factory=lambda x: PhoneNumber(value=x),
            on_success=Next(),
        ),
        state=states.CreateOrder.PHONE
    ),
    Window(
        Const("<b>⚠️Перевірте Ваше замовлення</b> \n"),

        Multi(
            Multi(
                Const("<b>💧 Вода:</b>"),
                Case(
                    {
                        "default_water": Const(DEFAULT_WATER_TYPE_TEXT),
                        "magnesia_water": Const(MAGNESIA_WATER_TYPE_TEXT)
                    },
                    selector=F["dialog_data"]["water_type"]
                ),
                sep=" "
            ),
            Format("<b>📦 Кількість:</b> {quantity}"),
            Jinja(
                "<b>🗓 Дата доставки:</b> "
                "{{dialog_data.delivery_date.strftime('%d.%m.%Y')}}"
            ),
            Multi(
                Const("<b>⏰ Час доставки:</b>"),
                Case(
                    {
                        "morning": Const(MORNING_TEXT),
                        "afternoon": Const(AFTERNOON_TEXT)
                    },
                    selector=F["dialog_data"]["delivery_time"]
                ),
                sep=" "
            ),
            Format("<b>🏠 Адреса:</b> {address}"),
            Multi(
                Const("<b>#️⃣ Квартира:</b>"),
                Case(
                    {
                        True: Const("Приватний будинок"),
                        False: Format("{apartment}")
                    },
                    selector=F["dialog_data"]["is_private_house"]
                ),
                sep=" "
            ),
            Jinja("<b>📞 Номер телефону:</b> {{dialog_data.phone}}"),
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
        getter=get_create_order_dialog_data,
    ),
    on_start=on_start_create_order_dialog,
    on_close=on_close_create_order_dialog
)

import operator
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Counter,
    ManagedCalendar,
    Next,
    Row,
    Select,
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from zoneinfo import ZoneInfo

from application.commands.order.create_order import (
    CreateOrderCommand,
    CreateOrderCommandHandler,
    OrderItemData,
)
from application.common.persistence.shop import ShopReader
from entities.order.models import DeliveryPreference
from entities.shop.models import ShopId
from presentation.common.consts import (
    ACTUAL_DELIVERY_TIME_PERIOD,
    BACK_BTN_TXT,
)
from presentation.common.helpers import default_on_start_handler
from presentation.common.widgets.common.calendar import CustomCalendar

from ..profile.main import get_profile_card
from ..profile.states import ProfileChangeAddress, ProfileChangePhone
from . import states
from .common import cart_getter, order_items_list


@inject
async def get_shop_info(
    shop_reader: FromDishka[ShopReader],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    shop_id: int = dialog_manager.middleware_data["shop_id"]

    shop = await shop_reader.read_with_id(ShopId(shop_id))
    if not shop:
        # TODO: error handling  # noqa: FIX002
        pass

    dialog_manager.dialog_data.update(
        {
            "regular_days_off": shop.regular_days_off,
            "special_days_off": [x.isoformat() for x in shop.special_days_off],
        }
    )

    return dialog_manager.dialog_data


async def on_date_selected(
    call: CallbackQuery,
    _widget: ManagedCalendar,
    manager: DialogManager,
    clicked_date: date,
) -> None:
    regular_days_off: list[int] = manager.dialog_data.get(
        "regular_days_off", []
    )
    special_days_off_dates: list[date] = [
        datetime.fromisoformat(day).date()
        for day in manager.dialog_data.get("special_days_off", [])
    ]

    is_regular_day_off = clicked_date.weekday() in regular_days_off
    is_special_day_off = clicked_date in special_days_off_dates

    if is_regular_day_off or is_special_day_off:
        await call.answer("❌ Доставка неможлива в вихідний день")
        return

    current_date = datetime.now(tz=ZoneInfo("Europe/Kiev")).date()
    if current_date > clicked_date:
        await call.answer("❌ Дата вибрана некорректно")
        return

    delta_days = abs((clicked_date - current_date).days)
    days_in_full_month = 31
    if delta_days >= days_in_full_month:
        await call.answer(
            "❌ Замовлення можна зробити максимум на місяць вперед"
        )
        return

    if (
        datetime.now(tz=ZoneInfo("Europe/Kiev")).time() > time(14, 0)
        and current_date == clicked_date
    ):
        await call.answer("❌ Замовлення приймаються до 14:00 поточного дня")
        return

    manager.dialog_data["order_date"] = clicked_date.isoformat()

    if manager.dialog_data.get("is_edit_mode", None):
        await manager.switch_to(state=states.CreateOrder.CONFIRMATION)
    else:
        await manager.next()


async def get_time_period(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    current_date = datetime.now(tz=ZoneInfo("Europe/Kiev")).date()
    selected_data = datetime.fromisoformat(
        dialog_manager.dialog_data["order_date"]
    )

    if selected_data == current_date:
        time_periods = [
            (DeliveryPreference.AFTERNOON, "Друга половина дня 🌃")
        ]
    else:
        time_periods = list(ACTUAL_DELIVERY_TIME_PERIOD.items())

    return {"time_periods": time_periods}


async def on_selected_time_period(
    _call: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
    selected: DeliveryPreference,
) -> None:
    manager.dialog_data["time_period"] = selected

    if manager.dialog_data.get("is_edit_mode", None):
        await manager.switch_to(state=states.CreateOrder.CONFIRMATION)
    else:
        await manager.next()


async def on_bottles_quantity_confirmation(
    _call: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
):
    bottles_quantity: int = manager.find("bottles_quantity").get_value()

    manager.dialog_data["bottles_quantity"] = bottles_quantity

    if manager.dialog_data.get("is_edit_mode", None):
        await manager.switch_to(state=states.CreateOrder.CONFIRMATION)
    else:
        await manager.next()


async def get_order_data(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    selected_date = dialog_manager.dialog_data["order_date"]
    order_date = datetime.fromisoformat(selected_date).date()

    order_time = ACTUAL_DELIVERY_TIME_PERIOD[
        dialog_manager.dialog_data["time_period"]
    ]
    bottles_quantity = dialog_manager.dialog_data["bottles_quantity"]
    address = dialog_manager.dialog_data["address"]
    phone = dialog_manager.dialog_data["phone_number"]

    return {
        "date": order_date,
        "time": order_time,
        "bottles": bottles_quantity,
        "address": address,
        "phone": phone,
    }


async def enable_edit_mode(
    _call: CallbackQuery, _widget: Button, manager: DialogManager
) -> None:
    manager.dialog_data["is_edit_mode"] = True


async def disable_edit_mode(
    _call: CallbackQuery, _widget: Button, manager: DialogManager
) -> None:
    if manager.dialog_data.get("is_edit_mode", None):
        manager.dialog_data.pop("is_edit_mode")


@inject
async def create_order(
    _call: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
    action: FromDishka[CreateOrderCommandHandler],
):
    shop_id: int = manager.middleware_data["shop_id"]
    selected_date = manager.dialog_data["order_date"]
    order_date = datetime.fromisoformat(selected_date).date()

    cart: dict[str, Any] = manager.dialog_data["cart"]

    order_items = [
        OrderItemData(
            quantity=int(item["quantity"]),
            price=Decimal(item["price_per_item"]),
            title=item["title"],
        )
        for item in cart.values()
    ]

    await action(
        CreateOrderCommand(
            shop_id=shop_id,
            bottles_to_exchange=manager.dialog_data["bottles_quantity"],
            delivery_date=order_date,
            delivery_preference=manager.dialog_data["time_period"],
            items=order_items,
        )
    )


create_order_dialog = Dialog(
    Window(
        Multi(
            Const("<b>Оберіть дату доставки</b>"),
            Const("<i>🟥 - вихідний день </i>"),
            sep="\n\n",
        ),
        CustomCalendar(id="order_data", on_click=on_date_selected),
        Cancel(Const(BACK_BTN_TXT)),
        getter=get_shop_info,
        state=states.CreateOrder.DATE,
    ),
    Window(
        Const("<b>Оберіть бажаний час доставки</b>"),
        Select(
            id="select_time_period",
            text=Format("{item[1]}"),
            items="time_periods",
            item_id_getter=operator.itemgetter(0),
            type_factory=lambda x: DeliveryPreference(x),
            on_click=on_selected_time_period,
        ),
        Back(Const(BACK_BTN_TXT)),
        getter=get_time_period,
        state=states.CreateOrder.TIME,
    ),
    Window(
        Const("<b>Вкажіть к-сть бутлів для обміну</b>"),
        Counter(id="bottles_quantity"),
        Button(
            Const("✅ Підтвердити"),
            on_click=on_bottles_quantity_confirmation,
            id="save_bottles_quantity",
        ),
        Back(Const(BACK_BTN_TXT)),
        state=states.CreateOrder.BOTTLE_QUANTITY,
    ),
    Window(
        Const(
            "Для замовлення Вам потрібно заповнити інформацію про Вашу адресу",
            when=~F["dialog_data"]["address"],
        ),
        Format(
            "<b>Адреса доставки:</b> <code>{dialog_data[address]}</code>",
            when=F["dialog_data"]["address"],
        ),
        Start(
            text=Const("Вказати адресу"),
            state=ProfileChangeAddress.NEW_ADDRESS,
            id="input_address",
            when=~F["dialog_data"]["address"],
        ),
        Next(text=Const("Далі"), when=F["dialog_data"]["address"]),
        Back(Const(BACK_BTN_TXT)),
        state=states.CreateOrder.ADDRESS,
    ),
    Window(
        Const(
            "Для замовлення Вам потрібно вказати контактний номер телефону",
            when=~F["dialog_data"]["phone_number"],
        ),
        Format(
            "<b>Контактний номер тефелона:</b> {dialog_data[phone_number]}",
            when=F["dialog_data"]["phone_number"],
        ),
        Start(
            text=Const("Вказати телефон"),
            state=ProfileChangePhone.NEW_PHONE,
            id="input_phone_number",
            when=~F["dialog_data"]["phone_number"],
        ),
        Next(text=Const("Далі"), when=F["dialog_data"]["phone_number"]),
        Back(Const(BACK_BTN_TXT)),
        state=states.CreateOrder.PHONE,
    ),
    Window(
        Const("👀 Перевірьте Ваше замовлення"),
        order_items_list,
        Multi(
            Multi(
                Format("📅 <b>Дата доставки:</b> {date}"),
                Format("🕐 <b>Час доставки:</b> {time}"),
                Format("♻️ <b>К-сть бутлів для обміну:</b> {bottles}"),
            ),
            Multi(
                Format("🛣 <b>Адреса доставки:</b> <code>{address}</code>"),
                Format("📞 <b>Контактний телефон:</b> {phone}"),
            ),
            sep="\n\n",
        ),
        Row(
            SwitchTo(
                text=Const("📅 Редагувати дату"),
                state=states.CreateOrder.DATE,
                id="edit_order_date",
                on_click=enable_edit_mode,
            ),
            SwitchTo(
                text=Const("🕐 Редагувати час"),
                state=states.CreateOrder.TIME,
                id="edit_order_time",
                on_click=enable_edit_mode,
            ),
        ),
        SwitchTo(
            text=Const("♻️ Редагувати к-сть на обмін"),
            state=states.CreateOrder.BOTTLE_QUANTITY,
            id="edit_bottles_quantity",
            on_click=enable_edit_mode,
        ),
        Button(
            id="confirm_order",
            text=Const("✅ Підтвердити замовлення"),
            on_click=create_order,  # noqa: ignore
        ),
        Back(Const(BACK_BTN_TXT), on_click=disable_edit_mode),
        state=states.CreateOrder.CONFIRMATION,
        getter=[cart_getter, get_order_data],
    ),
    on_start=default_on_start_handler,
    getter=get_profile_card,
)

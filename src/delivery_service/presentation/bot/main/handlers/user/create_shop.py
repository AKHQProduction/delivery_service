import operator
from typing import Any

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.input import (
    ManagedTextInput,
    MessageInput,
    TextInput,
)
from aiogram_dialog.widgets.kbd import (
    Cancel,
    ManagedMultiselect,
    Multiselect,
    Next,
    RequestLocation,
    Row,
)
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const, Format
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.commands.create_new_shop import (
    CreateNewShopRequest,
)
from delivery_service.application.common.factories.shop_factory import (
    DaysOffData,
)
from delivery_service.application.ports.location_finder import LocationFinder
from delivery_service.domain.shared.vo.address import CoordinatesData
from delivery_service.domain.staff.staff_role import Role
from delivery_service.infrastructure.integration.geopy.errors import (
    LocationNotFoundError,
)
from delivery_service.infrastructure.integration.telegram.const import (
    CREATE_SHOP_BTN,
)
from delivery_service.infrastructure.integration.telegram.kbd import (
    get_shop_staff_main_kbd,
)
from delivery_service.presentation.bot.widgets.kbd import get_back_btn

from . import states

CREATE_SHOP_ROUTER = Router()


@CREATE_SHOP_ROUTER.message(F.text == CREATE_SHOP_BTN)
async def setup_shop_creation_dialog(
    _: Message, dialog_manager: DialogManager
) -> None:
    await dialog_manager.start(
        state=states.ShopCreation.SHOP_NAME, mode=StartMode.RESET_STACK
    )


async def get_week_days(**_kwargs) -> dict[str, Any]:
    return {
        "days": [
            ("ПН", 0),
            ("ВТ", 1),
            ("СР", 2),
            ("ЧТ", 3),
            ("ПТ", 4),
            ("СБ", 5),
            ("НД", 6),
        ]
    }


async def get_all_input_data(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    multiselect: ManagedMultiselect | None = dialog_manager.find("week_days_s")
    if not multiselect:
        raise ValueError()

    days_id = sorted([int(x) for x in multiselect.get_checked()])
    week_days: list[tuple[str, int]] = (await get_week_days())["days"]
    selected_days_off = [
        day[0].lower() for day in week_days if day[1] in days_id
    ]

    dialog_manager.dialog_data.update({"days_off": days_id})

    return {
        "shop_name": dialog_manager.dialog_data.get("shop_name"),
        "days_off": ", ".join(selected_days_off)
        if len(selected_days_off) > 0
        else "без вихідних",
        "latitude": dialog_manager.dialog_data.get("latitude"),
        "longitude": dialog_manager.dialog_data.get("longitude"),
    }


async def clear_days_off(
    _: CallbackQuery, __: Widget, manager: DialogManager
) -> None:
    multiselect: ManagedMultiselect | None = manager.find("week_days_s")
    if not multiselect:
        return

    await multiselect.reset_checked()


@inject
async def on_confirm_new_shop_creation(
    call: CallbackQuery,
    __: Widget,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    data = manager.dialog_data

    await sender.send(
        CreateNewShopRequest(
            shop_name=data.get("shop_name"),  # pyright: ignore[reportArgumentType]
            shop_coordinates=CoordinatesData(
                latitude=data.get("latitude"),  # pyright: ignore[reportArgumentType]
                longitude=data.get("longitude"),  # pyright: ignore[reportArgumentType]
            ),
            days_off=DaysOffData(regular_days=data.get("days_off")),  # pyright: ignore[reportArgumentType]
        )
    )

    await call.message.answer(  # pyright: ignore[reportOptionalMemberAccess]
        "✅ Магазин створено",
        reply_markup=get_shop_staff_main_kbd(roles=[Role.SHOP_OWNER]),
    )


async def on_input_shop_name(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data.update({"shop_name": value})

    await manager.next()


async def on_share_shop_location(
    msg: Message, _: MessageInput, manager: DialogManager
) -> None:
    if msg.location:
        manager.dialog_data.update(
            {
                "latitude": msg.location.latitude,
                "longitude": msg.location.longitude,
            }
        )
        return await manager.next()
    raise ValueError()


@inject
async def on_input_shop_location(
    msg: Message,
    __: MessageInput,
    manager: DialogManager,
    location_finder: FromDishka[LocationFinder],
) -> Message | None:
    if msg.text:
        try:
            coordinates = await location_finder.find_location(msg.text)
        except LocationNotFoundError:
            return await msg.answer(
                "Адресу не найдено.\n"
                "Введіть повторно або поділіться локацією 👇"
            )

        manager.dialog_data.update(
            {
                "latitude": coordinates.latitude,
                "longitude": coordinates.longitude,
            }
        )
        return await manager.next()
    raise ValueError()


SHOP_CREATION_DIALOG = Dialog(
    Window(
        Const("1️⃣ Введіть назву магазину"),
        TextInput(id="shop_name_input", on_success=on_input_shop_name),
        get_back_btn(back_to_prev_dialog=True),
        state=states.ShopCreation.SHOP_NAME,
    ),
    Window(
        Const("2️⃣ Вкажіть вихідні дні"),
        Row(
            Multiselect(
                id="week_days_s",
                checked_text=Format("✓ {item[0]}"),
                unchecked_text=Format("{item[0]}"),
                items="days",
                item_id_getter=operator.itemgetter(1),
            )
        ),
        Next(id="to_input_shop_location", text=Const("➡️ Далі")),
        get_back_btn(on_click=clear_days_off),
        getter=get_week_days,
        state=states.ShopCreation.SHOP_DAYS_OFF,
    ),
    Window(
        Const("3️⃣ Вкажіть адресу магазину або поділіться нею\n"),
        Const(
            "<i>Якщо виникли складноші - перевірте вашу адресу"
            " на карті: https://www.openstreetmap.org</i>"
        ),
        MessageInput(filter=F.location, func=on_share_shop_location),
        MessageInput(filter=F.text, func=on_input_shop_location),
        RequestLocation(Const("📍 Поділитися локацієй")),
        Next(
            id="to_preview",
            text=Const("➡️ Далі"),
            when=F["dialog_data"]["latitude"],
        ),
        get_back_btn(),
        markup_factory=ReplyKeyboardFactory(
            resize_keyboard=True, one_time_keyboard=True
        ),
        state=states.ShopCreation.SHOP_LOCATION,
    ),
    Window(
        Const("Магазин буде створенний з такими данними 👇\n"),
        Format(
            "<b>Ім'я:</b> {shop_name}\n"
            "<b>Вихідні:</b> {days_off} \n"
            "<b>Координати:</b> довгота - {longitude}, широта - {latitude}"
        ),
        Cancel(
            text=Const("✅ Підтвердити"), on_click=on_confirm_new_shop_creation
        ),
        get_back_btn(back_to_prev_dialog=True, btn_text="❌ Відхилити"),
        getter=get_all_input_data,
        state=states.ShopCreation.PREVIEW,
    ),
)

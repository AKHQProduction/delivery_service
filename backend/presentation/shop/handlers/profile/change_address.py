from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Data, Dialog, DialogManager, Window
from aiogram_dialog.api.internal import ReplyCallbackQuery
from aiogram_dialog.widgets.input import (
    ManagedTextInput,
    MessageInput,
    TextInput,
)
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Next,
    RequestLocation,
    Row,
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.geo import GeoProcessor
from application.profile.commands.update_address_by_yourself import (
    ChangeAddress,
    ChangeAddressInputData,
)
from infrastructure.geopy.errors import (
    InvalidAddressInputError,
)
from presentation.common.consts import BACK_BTN_TXT, CANCEL_BTN_TXT
from presentation.common.helpers import (
    default_on_start_handler,
    parse_address,
    send_main_keyboard,
)

from . import states


async def on_input_apartment_number(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: int
) -> None:
    manager.dialog_data["apartment_data"] = value

    await manager.next()


async def on_input_floor(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: int
) -> None:
    manager.dialog_data["floor_data"] = value

    await manager.next()


async def on_input_intercom_code(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: int
) -> None:
    manager.dialog_data["intercom_code_data"] = value

    await manager.next()


async def get_all_address_data(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    address_data = parse_address(dialog_manager.dialog_data["address"])

    address_data.update(
        {
            "apartment_number": dialog_manager.dialog_data.get(
                "apartment_data", "приватний будинок"
            ),
            "floor": dialog_manager.dialog_data.get("floor_data", "-"),
            "intercom_code": dialog_manager.dialog_data.get(
                "intercom_code_data", "-"
            ),
        }
    )

    return address_data


@inject
async def accept_update_address_in_profile(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
    action: FromDishka[ChangeAddress],
) -> None:
    address_data = parse_address(manager.dialog_data["address"])

    await action(
        ChangeAddressInputData(
            city=address_data.get("city"),
            street=address_data.get("street"),
            house_number=address_data.get("house_number"),
            apartment_number=manager.dialog_data.get("apartment_data"),
            floor=manager.dialog_data.get("floor_data"),
            intercom_code=manager.dialog_data.get("intercom_code_data"),
        )
    )


async def on_after_successfully_input_address(
    _: Data, result: Any, manager: DialogManager
):
    if result:
        manager.dialog_data["address"] = result["address"]

        await manager.switch_to(
            state=states.ProfileChangeAddress.APARTMENT_NUMBER
        )


change_address_dialog = Dialog(
    Window(
        Const("Виберіть спосіб зміни адреси"),
        Start(
            id="send_location_from_user",
            text=Const("✍️ Вказати адресу"),
            state=states.AddressInputByUser.INPUT_LOCATION,
        ),
        Start(
            id="send_location_from_tg",
            text=Const("📍 Поділитись адресою"),
            state=states.AddressInputByTg.SEND_LOCATION,
        ),
        Cancel(Const(BACK_BTN_TXT)),
        state=states.ProfileChangeAddress.NEW_ADDRESS,
    ),
    Window(
        Const("Введіть номер вашої квартири"),
        TextInput(
            id="apartment_number_input",
            type_factory=int,
            on_success=on_input_apartment_number,
        ),
        SwitchTo(
            Const("Це приватний будинок"),
            id="private_house",
            state=states.ProfileChangeAddress.CONFIRMATION,
        ),
        state=states.ProfileChangeAddress.APARTMENT_NUMBER,
    ),
    Window(
        Const("Введіть Ваш поверх"),
        TextInput(
            id="floor_input", type_factory=int, on_success=on_input_floor
        ),
        state=states.ProfileChangeAddress.FLOOR,
    ),
    Window(
        Const("Введіть код від домофону"),
        TextInput(
            id="intercom_code_input",
            type_factory=int,
            on_success=on_input_intercom_code,
        ),
        Next(Const("Відсутній")),
        state=states.ProfileChangeAddress.INTERCOM_CODE,
    ),
    Window(
        Multi(
            Const("Ваша нова адреса буде виглядати так:"),
            Multi(
                Format("Місто: {city}"),
                Format("Вулиця: {street}"),
                Format("Номер будинку: {house_number}"),
                Format("Номер квартири: {apartment_number}"),
                Format("Поверх: {floor}"),
                Format("Код від домофону: {intercom_code}"),
            ),
            Const("Підтвердіть зміну адреси"),
            sep="\n\n",
        ),
        Cancel(
            Const("Так"),
            id="accept_change_address",
            on_click=accept_update_address_in_profile,  # noqa: ignore
        ),
        Cancel(
            Const("Ні"),
            id="reject_change_address",
        ),
        state=states.ProfileChangeAddress.CONFIRMATION,
        getter=get_all_address_data,
    ),
    on_start=default_on_start_handler,
    on_process_result=on_after_successfully_input_address,
)


@inject
async def on_input_user_location_from_tg(
    msg: Message,
    _: MessageInput,
    manager: DialogManager,
    geo: FromDishka[GeoProcessor],
) -> None:
    coordinates = (msg.location.latitude, msg.location.longitude)

    try:
        output_data = await geo.get_location_with_coordinates(coordinates)
    except InvalidAddressInputError:
        await msg.answer("Не вдалось знайти вашої адреси, повторіть спробу")
    else:
        manager.dialog_data["address"] = output_data
        await send_main_keyboard(manager, "⏳")
        await manager.next()


async def on_close_send_location_dialog(
    msg: ReplyCallbackQuery,
    _: Button,
    manager: DialogManager,
):
    await msg.original_message.delete()

    await send_main_keyboard(manager, "⏳")


async def on_accept_find_address(
    _: CallbackQuery, __: Button, manager: DialogManager
) -> None:
    await manager.done({"address": manager.dialog_data["address"]})


send_address_by_telegram_dialog = Dialog(
    Window(
        Const("Відправте Вашу геопозицію або виберіть локацію на мапі"),
        MessageInput(
            filter=F.location,
            func=on_input_user_location_from_tg,  # noqa: ignore
        ),
        RequestLocation(Const("📍 Поділитися адресою")),
        Cancel(
            Const(CANCEL_BTN_TXT),
            on_click=on_close_send_location_dialog,  # noqa: ignore
        ),
        markup_factory=ReplyKeyboardFactory(resize_keyboard=True),
        state=states.AddressInputByTg.SEND_LOCATION,
    ),
    Window(
        Format("Ваша адреса: <code>{dialog_data[address]}</code>?"),
        Row(
            Button(
                id="back_to_confirmation_change",
                text=Const("Так"),
                on_click=on_accept_find_address,
            ),
            Back(Const("Ні")),
        ),
        state=states.AddressInputByTg.CONFIRMATION,
    ),
)


@inject
async def on_input_address_from_user(
    msg: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
    geo: FromDishka[GeoProcessor],
) -> None:
    try:
        output_data = await geo.get_location_with_row(value)
    except InvalidAddressInputError:
        await msg.answer("Не вдалось знайти вашої адреси, повторіть спробу")
    else:
        await manager.done({"address": output_data})


send_address_by_user_dialog = Dialog(
    Window(
        Multi(
            Const("Введіть Вашу адресу"),
            Const("<i>Наприклад: Черкаси бульвар Шевченка 123</i>"),
        ),
        TextInput(
            id="on_input_address_from_user",
            on_success=on_input_address_from_user,  # noqa: ignore
        ),
        Cancel(Const(BACK_BTN_TXT)),
        state=states.AddressInputByUser.INPUT_LOCATION,
    )
)

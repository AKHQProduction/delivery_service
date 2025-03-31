from dataclasses import dataclass

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.input import (
    ManagedTextInput,
    MessageInput,
    TextInput,
)
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    ManagedMultiselect,
    Multiselect,
    Next,
    RequestLocation,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.markup.reply_keyboard import ReplyKeyboardFactory
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.commands.bot.admin_bot_start import (
    AdminBotStartCommandHandler,
)
from application.commands.shop.create_shop import (
    CreateShopCommand,
    CreateShopCommandHandler,
)
from application.common.errors.shop import ShopAlreadyExistsError
from application.common.geo import GeoProcessor
from application.common.identity_provider import IdentityProvider
from application.common.specs.length import HasGreateLength, HasLessLength
from application.common.specs.pattern import MatchPattern
from application.common.specs.value import Greate
from application.common.webhook_manager import TokenVerifier
from infrastructure.tg.errors import ShopTokenUnauthorizedError
from presentation.common.consts import CANCEL_BTN_TXT, CREATE_SHOP_BTN_TXT
from presentation.common.helpers import step_toggler_in_form
from presentation.common.widgets.common.cancel_btn import (
    back_to_main_menu_btn,
    dialog_has_mistakes_in_input,
    setup_input_error_flag,
)

from ...common.start import cmd_start
from . import states

router = Router()


@router.message(F.text == CREATE_SHOP_BTN_TXT)
async def create_shop_handler(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.CreateShopStates.TITLE, mode=StartMode.RESET_STACK
    )


cancel_btn_when = back_to_main_menu_btn(
    CANCEL_BTN_TXT, when=dialog_has_mistakes_in_input
)
cancel_btn = back_to_main_menu_btn(CANCEL_BTN_TXT)
back_to_main_menu_btn = back_to_main_menu_btn("🔙 Головне меню")


async def check_after_success_input_shop_title(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    criteria = HasLessLength(3) | HasGreateLength(20)

    if criteria.is_satisfied_by(value):
        setup_input_error_flag(manager, flag=True)
    else:
        setup_input_error_flag(manager, flag=False)

        manager.dialog_data["shop_title"] = value

        await step_toggler_in_form(
            manager, "form_is_completed", states.CreateShopStates.REVIEW
        )


@inject
async def check_after_success_input_shop_token(
    _: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
    token_verifier: FromDishka[TokenVerifier],
) -> None:
    criteria = MatchPattern(r"^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$")

    if criteria.is_satisfied_by(value):
        try:
            await token_verifier.verify(value)
        except ShopTokenUnauthorizedError:
            setup_input_error_flag(manager, flag=True)
        else:
            setup_input_error_flag(manager, flag=False)

            manager.dialog_data["shop_token"] = value

            await manager.next()
    else:
        setup_input_error_flag(manager, flag=True)


@dataclass
class WeekDay:
    id: int
    name: str


async def week_day_getter(**_kwargs) -> dict:
    return {
        "week_days": [
            WeekDay(id=0, name="ПН"),
            WeekDay(id=1, name="ВТ"),
            WeekDay(id=2, name="СР"),
            WeekDay(id=3, name="ЧТ"),
            WeekDay(id=4, name="ПТ"),
            WeekDay(id=5, name="СБ"),
            WeekDay(id=6, name="НД"),
        ]
    }


def week_day_id_getter(week_day: WeekDay) -> int:
    return week_day.id


async def check_after_success_input_delivery_distance(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: int
) -> None:
    criteria = Greate(0)

    if criteria.is_satisfied_by(value):
        setup_input_error_flag(manager, flag=False)

        manager.dialog_data["shop_delivery_distance"] = value

        await step_toggler_in_form(
            manager, "form_is_completed", states.CreateShopStates.REVIEW
        )
    else:
        setup_input_error_flag(manager, flag=True)


@inject
async def on_input_shop_location(
    msg: Message,
    _: MessageInput,
    manager: DialogManager,
    geo: FromDishka[GeoProcessor],
):
    location = await geo.get_location_with_coordinates(
        (msg.location.latitude, msg.location.longitude)
    )

    manager.dialog_data["coordinates"] = (
        msg.location.latitude,
        msg.location.longitude,
    )
    manager.dialog_data["location"] = location

    await step_toggler_in_form(
        manager, "form_is_completed", states.CreateShopStates.REVIEW
    )


@inject
async def on_reject_input_location(
    call: CallbackQuery,
    _: Button,
    manager: DialogManager,
    action: FromDishka[AdminBotStartCommandHandler],
    id_provider: FromDishka[IdentityProvider],
):
    bot: Bot = manager.middleware_data["bot"]

    await cmd_start(call, bot, action, id_provider)


async def create_shop_form_getter(
    dialog_manager: DialogManager, **_kwargs
) -> dict:
    regular_days_selector: ManagedMultiselect = dialog_manager.find(
        "new_shop_regular_day_off_select"
    )

    days_id = [int(x) for x in regular_days_selector.get_checked()]

    week_days: list = (await week_day_getter())["week_days"]

    selected_days = [
        day.name.lower() for day in week_days if day.id in days_id
    ]

    dialog_manager.dialog_data["selected_days"] = (
        ",".join(selected_days) if len(selected_days) > 0 else "без вихідних"
    )

    dialog_manager.dialog_data["regular_days"] = days_id

    dialog_manager.dialog_data["form_is_completed"] = True

    return dialog_manager.dialog_data


@inject
async def on_accept_shop_creation_form(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    create_shop: FromDishka[CreateShopCommandHandler],
):
    await call.message.delete()

    wait_emoji_msg = await call.message.answer("⏳")

    data = manager.dialog_data

    try:
        await create_shop(
            CreateShopCommand(
                title=data["shop_title"],
                token=data["shop_token"],
                delivery_distance=data["shop_delivery_distance"],
                location=data["coordinates"],
                regular_days_off=data["regular_days"],
            )
        )
    except ShopAlreadyExistsError:
        await wait_emoji_msg.delete()
        await call.message.answer("Токен бота уже використовується")
    else:
        await wait_emoji_msg.delete()

        await manager.next()


create_shop_dialog = Dialog(
    Window(
        Multi(
            Const("1️⃣ Введіть назву магазину"),
            Const(
                "❗Назва повинна містити <b>щонайменше 3 символи</b>, "
                "але <b>не більше 20.</b>"
            ),
            sep="\n\n",
        ),
        TextInput(
            id="new_shop_title_input",
            on_success=check_after_success_input_shop_title,
        ),
        cancel_btn_when,
        state=states.CreateShopStates.TITLE,
    ),
    Window(
        Const("2️⃣ Введіть токен Вашого магазину"),
        TextInput(
            id="new_shop_token_input",
            on_success=check_after_success_input_shop_token,  # noqa: ignore
        ),
        cancel_btn_when,
        state=states.CreateShopStates.TOKEN,
    ),
    Window(
        Const("3️⃣ Вкажіть вихідні дні Вашого магазину, можна обрати декілька"),
        Row(
            Multiselect(
                checked_text=Format("✓ {item.name}"),
                unchecked_text=Format("{item.name}"),
                id="new_shop_regular_day_off_select",
                items="week_days",
                item_id_getter=week_day_id_getter,
            )
        ),
        Next(
            Const("Далі"),
            show_mode=ShowMode.SEND,
            when=~F["dialog_data"]["form_is_completed"],
        ),
        SwitchTo(
            Const("Далі"),
            id="regular_days_switch",
            show_mode=ShowMode.SEND,
            when=F["dialog_data"]["form_is_completed"],
            state=states.CreateShopStates.REVIEW,
        ),
        getter=week_day_getter,
        state=states.CreateShopStates.DAYS_OFF,
    ),
    Window(
        Const("4️⃣ Вкажіть максимальний кілометраж доставки"),
        TextInput(
            id="new_shop_delivery_distance",
            type_factory=int,
            on_success=check_after_success_input_delivery_distance,
        ),
        cancel_btn_when,
        state=states.CreateShopStates.DELIVERY_DISTANCE,
    ),
    Window(
        Const("5️⃣ Відмітьте ваш магазин на карті і надішліть"),
        MessageInput(
            filter=F.location,
            func=on_input_shop_location,  # noqa: igore
        ),
        RequestLocation(Const("📍 Поділитися локацієй")),
        Cancel(
            Const(CANCEL_BTN_TXT),
            on_click=on_reject_input_location,  # noqa: igore
        ),
        markup_factory=ReplyKeyboardFactory(
            resize_keyboard=True, one_time_keyboard=True
        ),
        state=states.CreateShopStates.LOCATION,
    ),
    Window(
        Multi(
            Const("Перевірьте введені данні👇"),
            Multi(
                Format("🏪 <b>Назва магазину:</b> {shop_title}"),
                Const("🔑 <b>Токен:</b> перевірений"),
                Format("📅 <b>Вихідні дні:</b> {selected_days}"),
                Format(
                    "📏 <b>Макс. відстань доставки:</b> "
                    "{shop_delivery_distance} км"
                ),
                Format("📍 <b>Локація:</b> {location}"),
            ),
            sep="\n\n",
        ),
        Row(
            SwitchTo(
                id="edit_shop_title_btn",
                text=Const("Змінити назву"),
                state=states.CreateShopStates.TITLE,
            ),
            SwitchTo(
                id="edit_shop_regular_days_off_btn",
                text=Const("Змінити вихідні дні"),
                state=states.CreateShopStates.DAYS_OFF,
            ),
        ),
        Row(
            SwitchTo(
                id="edit_shop_delivery_distance_btn",
                text=Const("Змінити відстань доставки"),
                state=states.CreateShopStates.DELIVERY_DISTANCE,
            ),
            SwitchTo(
                id="edit_shop_location_btn",
                text=Const("Змінити локацію"),
                state=states.CreateShopStates.LOCATION,
            ),
        ),
        Button(
            text=Const("✅ Підтвердити"),
            id="accept_shop_creation_form",
            on_click=on_accept_shop_creation_form,  # noqa: ignore
        ),
        cancel_btn,
        state=states.CreateShopStates.REVIEW,
        getter=create_shop_form_getter,
    ),
    Window(
        Multi(
            Const(
                "Ви успішно створили магазин, "
                "для перевірки введіть команду /start в своєму боті"
            ),
            Const("Дякуєм, що обрали наш сервіс"),
            sep="\n\n",
        ),
        back_to_main_menu_btn,
        state=states.CreateShopStates.FINISH,
    ),
)

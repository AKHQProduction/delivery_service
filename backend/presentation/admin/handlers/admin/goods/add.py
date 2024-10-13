import base64
import operator
from decimal import Decimal, InvalidOperation
from typing import Any

from aiogram import F
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import (
    ManagedTextInput,
    MessageInput,
    TextInput,
)
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Cancel,
    Column,
    Next,
    Row,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.specs.length import HasGreateLength, HasLessLength
from application.goods.input_data import FileMetadata
from application.goods.interactors.add_goods import AddGoods, AddGoodsInputData
from entities.goods.models import GoodsType
from presentation.common.consts import (
    ACTUAL_GOODS_TYPES,
    BACK_BTN_TXT,
    CANCEL_BTN_TXT,
)
from presentation.common.getters.goods import get_goods_types
from presentation.common.helpers import step_toggler_in_form

from . import states
from .common import photo_getter


async def on_input_title(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    criteria = HasGreateLength(2) and HasLessLength(21)

    if criteria.is_satisfied_by(value):
        manager.dialog_data["title"] = value

        await step_toggler_in_form(
            manager, "form_is_completed", states.AddNewGoods.PREVIEW
        )


async def on_input_price(
    msg: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    try:
        price = Decimal(value)
    except InvalidOperation:
        await msg.answer("Потрібно ввести число")
    else:
        if price > 0:
            manager.dialog_data["price"] = str(price)

            await step_toggler_in_form(
                manager, "form_is_completed", states.AddNewGoods.PREVIEW
            )


async def on_goods_type_selected(
    _: CallbackQuery, __: Any, manager: DialogManager, value: GoodsType
) -> None:
    manager.dialog_data["type"] = value
    manager.dialog_data["type_text"] = ACTUAL_GOODS_TYPES[value]

    await step_toggler_in_form(
        manager, "form_is_completed", states.AddNewGoods.PREVIEW
    )


async def goods_photo_handler(
    msg: Message, _: MessageInput, manager: DialogManager
) -> None:
    await msg.delete()

    photo = msg.photo[-1]

    file_info = await msg.bot.get_file(photo.file_id)

    file_bytes = await msg.bot.download_file(file_info.file_path)

    photo_bytes = file_bytes.read()

    manager.dialog_data["file_id"] = file_info.file_id
    manager.dialog_data["bytes"] = base64.b64encode(photo_bytes).decode(
        "utf-8"
    )

    await manager.next()


async def on_without_photo_btn(
    _: CallbackQuery, __: Button, manager: DialogManager
) -> None:
    if manager.dialog_data.get("file_id"):
        manager.dialog_data.pop("file_id")
        manager.dialog_data.pop("photo_bytes")


@inject
async def on_accept_add_new_goods(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
    action: FromDishka[AddGoods],
) -> None:
    metadata = (
        FileMetadata(base64.b64decode(manager.dialog_data["bytes"]))
        if manager.dialog_data.get("bytes")
        else None
    )

    await action(
        AddGoodsInputData(
            title=manager.dialog_data["title"],
            price=Decimal(manager.dialog_data["price"]),
            goods_type=manager.dialog_data["type"],
            metadata=metadata,
        )
    )


async def get_all_add_goods_dialog_data(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    dialog_manager.dialog_data["form_is_completed"] = True

    return dialog_manager.dialog_data


add_new_goods_dialog = Dialog(
    Window(
        Const("1️⃣ <b>Введіть назву товару</b>"),
        Const("<i>Довжина повинна бути від 3 символів до 20 включно</i>"),
        TextInput(id="title_input", on_success=on_input_title),
        Cancel(Const(BACK_BTN_TXT)),
        state=states.AddNewGoods.TITLE,
    ),
    Window(
        Const("2️⃣ <b>Введіть ціну товара</b>"),
        Const("<i>Ціна повинна бути більша 0</i>"),
        TextInput(id="title_input", on_success=on_input_price),
        Back(Const(BACK_BTN_TXT)),
        state=states.AddNewGoods.PRICE,
    ),
    Window(
        Const("3️⃣ <b>Виберіть тип товара</b>"),
        Select(
            id="select_goods_type",
            text=Format("{item[1]}"),
            items="types",
            item_id_getter=operator.itemgetter(0),
            type_factory=lambda item: GoodsType(item),
            on_click=on_goods_type_selected,
        ),
        Back(Const(BACK_BTN_TXT)),
        state=states.AddNewGoods.GOODS_TYPE,
        getter=get_goods_types,
    ),
    Window(
        Const("4️⃣ <b>Відправте фото товара</b>"),
        MessageInput(goods_photo_handler, content_types=ContentType.PHOTO),
        Next(Const("Без фото"), on_click=on_without_photo_btn),
        Back(Const(BACK_BTN_TXT)),
        state=states.AddNewGoods.METADATA,
    ),
    Window(
        DynamicMedia(selector="media", when=F["media"]),
        Multi(
            Const("Перевірте введені дані"),
            Multi(
                Format("🏷 <b>Назва:</b> {title}"),
                Format("💸 <b>Ціна:</b> {price} UAH"),
                Format("📜 <b>Категорія:</b> {type_text}"),
            ),
            Const("Зберегти товар в асортимент магазину?"),
            sep="\n\n",
        ),
        Row(
            SwitchTo(
                id="edit_goods_title",
                text=Const("🏷 Змінити назву"),
                state=states.AddNewGoods.TITLE,
            ),
            SwitchTo(
                id="edit_goods_price",
                text=Const("💸 Змінити ціну"),
                state=states.AddNewGoods.PRICE,
            ),
        ),
        Row(
            SwitchTo(
                id="edit_goods_type",
                text=Const("📜 Змінити категорію"),
                state=states.AddNewGoods.GOODS_TYPE,
            ),
            SwitchTo(
                id="edit_goods_photo",
                text=Const("🖼 Змінити фото"),
                state=states.AddNewGoods.METADATA,
            ),
        ),
        Column(
            Cancel(
                Const("✅ Зберегти"),
                on_click=on_accept_add_new_goods,  # noqa: ignore
            ),
            Cancel(Const(CANCEL_BTN_TXT)),
        ),
        state=states.AddNewGoods.PREVIEW,
        getter=[get_all_add_goods_dialog_data, photo_getter],
    ),
)

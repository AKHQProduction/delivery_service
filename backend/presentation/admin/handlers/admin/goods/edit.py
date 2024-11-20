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
    Button,
    Cancel,
    Group,
    Row,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.specs.length import HasGreateLength, HasLessLength
from application.goods.input_data import FileMetadata
from application.goods.interactors.edit_goods import (
    EditGoods,
    EditGoodsInputData,
)
from application.goods.interactors.get_goods import GetGoods, GetGoodsInputData
from entities.goods.models import GoodsType
from presentation.common.consts import ACTUAL_GOODS_TYPES, BACK_BTN_TXT
from presentation.common.getters.goods import (
    get_goods_types,
    goods_card_photo,
    goods_card_txt,
    photo_getter,
)

from . import states


@inject
async def on_edit_btn(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
    action: FromDishka[EditGoods],
) -> None:
    goods_id = manager.dialog_data["goods_id"]

    title = manager.dialog_data["title"]
    price = Decimal(manager.dialog_data["price"])
    category_type = manager.dialog_data["category_type"]

    # If there was a photo, but it was deleted
    if manager.dialog_data.get("photo_is_deleted"):
        metadata = None
    # If the photo was/is not there and it has been replaced
    elif manager.dialog_data.get("is_new_photo"):
        bytes_data = manager.dialog_data["bytes"]
        metadata = FileMetadata(payload=base64.b64decode(bytes_data))
    # If there was no photo and no new one has been added
    else:
        metadata = FileMetadata(payload=None)

    await action(
        EditGoodsInputData(
            goods_id=goods_id,
            title=title,
            price=price,
            goods_type=category_type,
            metadata=metadata,
        )
    )


edit_goods_kb = Group(
    Row(
        SwitchTo(
            Const("🏷 Змінити назву"),
            id="edit_goods_title",
            state=states.EditGoods.TITLE,
        ),
        SwitchTo(
            Const("💸 Змінити ціну"),
            id="edit_goods_price",
            state=states.EditGoods.PRICE,
        ),
    ),
    Row(
        SwitchTo(
            Const("📜 Змінити категорію"),
            id="edit_goods_type",
            state=states.EditGoods.GOODS_TYPE,
        ),
        SwitchTo(
            Const("🖼 Змінити фото"),
            id="edit_goods_pic",
            state=states.EditGoods.METADATA,
        ),
    ),
    Cancel(
        id="save_after_edit_goods",
        text=Const("💾 Зберегти"),
        on_click=on_edit_btn,  # noqa: ignore
        when=F["dialog_data"]["is_edited"],
    ),
    Cancel(Const(BACK_BTN_TXT)),
)

back_to_start_edit = SwitchTo(
    Const(BACK_BTN_TXT),
    state=states.EditGoods.START,
    id="back_to_start_edit_menu",
)


async def on_successfully_input(
    key: str, value: str, manager: DialogManager
) -> None:
    manager.dialog_data[key] = value
    manager.dialog_data["is_edited"] = True

    await manager.switch_to(state=states.EditGoods.START)


async def on_input_new_goods_title(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    criteria = HasGreateLength(2) and HasLessLength(21)

    if criteria.is_satisfied_by(value):
        await on_successfully_input("title", value, manager)


async def on_input_new_goods_price(
    msg: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    try:
        price = Decimal(value)
    except InvalidOperation:
        await msg.answer("Потрібно ввести число")
    else:
        if price > 0:
            await on_successfully_input("price", str(price), manager)


async def on_goods_type_selected(
    _: CallbackQuery, __: Any, manager: DialogManager, value: GoodsType
) -> None:
    manager.dialog_data["category_type"] = value

    await on_successfully_input("category", ACTUAL_GOODS_TYPES[value], manager)


async def on_goods_photo_input(
    msg: Message, _: MessageInput, manager: DialogManager
) -> None:
    await msg.delete()

    manager.dialog_data["is_new_photo"] = True

    if manager.dialog_data.get("path"):
        manager.dialog_data.pop("path")

    photo = msg.photo[-1]

    file_info = await msg.bot.get_file(photo.file_id)

    file_bytes = await msg.bot.download_file(file_info.file_path)

    photo_bytes = file_bytes.read()

    manager.dialog_data["bytes"] = base64.b64encode(photo_bytes).decode(
        "utf-8"
    )

    await on_successfully_input("file_id", file_info.file_id, manager)


async def on_without_photo_btn(
    _: CallbackQuery, __: Button, manager: DialogManager
) -> None:
    if manager.dialog_data.get("path"):
        manager.dialog_data.pop("path")

        manager.dialog_data["is_edited"] = True
        manager.dialog_data["photo_is_deleted"] = True

    if manager.dialog_data.get("file_id"):
        manager.dialog_data.pop("file_id")
        manager.dialog_data.pop("photo_bytes")


@inject
async def on_start_view_dialog(
    data: dict[str, Any], manager: DialogManager, action: FromDishka[GetGoods]
) -> None:
    goods_id = data["goods_id"]

    goods = await action(GetGoodsInputData(goods_id))

    title = str(goods.title)
    price = str(goods.price)
    category_type = goods.goods_type
    category = ACTUAL_GOODS_TYPES[category_type]
    path = goods.metadata_path

    manager.dialog_data["goods_id"] = goods_id
    manager.dialog_data["title"] = title
    manager.dialog_data["price"] = price
    manager.dialog_data["category_type"] = category_type
    manager.dialog_data["category"] = category
    manager.dialog_data["path"] = path


edit_goods_dialog = Dialog(
    Window(
        goods_card_photo,
        Multi(goods_card_txt, Const("Виберіть дію 👇"), sep="\n\n"),
        edit_goods_kb,
        state=states.EditGoods.START,
    ),
    Window(
        goods_card_photo,
        Multi(
            goods_card_txt,
            Const("<b>Введіть нову назву товара</b> 👇"),
            sep="\n\n",
        ),
        TextInput(
            id="new_goods_title_input", on_success=on_input_new_goods_title
        ),
        back_to_start_edit,
        state=states.EditGoods.TITLE,
    ),
    Window(
        goods_card_photo,
        Multi(
            goods_card_txt,
            Const(
                "<b>Введіть нову ціну товара</b> 👇\n"
                "<i>Ціна повинна бути більша 0</i>"
            ),
            sep="\n\n",
        ),
        TextInput(id="new_goods_price", on_success=on_input_new_goods_price),
        back_to_start_edit,
        state=states.EditGoods.PRICE,
    ),
    Window(
        goods_card_photo,
        Multi(
            goods_card_txt, Const("<b>Виберіть тип товара</b> 👇"), sep="\n\n"
        ),
        Select(
            id="select_goods_type",
            text=Format("{item[1]}"),
            items="types",
            item_id_getter=operator.itemgetter(0),
            type_factory=lambda item: GoodsType(item),
            on_click=on_goods_type_selected,
        ),
        back_to_start_edit,
        state=states.EditGoods.GOODS_TYPE,
        getter=get_goods_types,
    ),
    Window(
        goods_card_photo,
        Multi(
            goods_card_txt,
            Const("<b>Відправте нове фото товару</b> 👇"),
            sep="\n\n",
        ),
        MessageInput(on_goods_photo_input, content_types=ContentType.PHOTO),
        SwitchTo(
            id="without_photo_btn",
            text=(Const("Без фото")),
            state=states.EditGoods.START,
            on_click=on_without_photo_btn,
        ),
        back_to_start_edit,
        state=states.EditGoods.METADATA,
    ),
    on_start=on_start_view_dialog,  # noqa: ignore
    getter=photo_getter,
)

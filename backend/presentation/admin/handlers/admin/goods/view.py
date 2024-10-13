from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Next, Row
from aiogram_dialog.widgets.text import Const, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.goods.interactors.delete_goods import (
    DeleteGoods,
    DeleteGoodsInputData,
)
from application.goods.interactors.get_goods import GetGoods, GetGoodsInputData
from presentation.common.consts import ACTUAL_GOODS_TYPES, BACK_BTN_TXT
from presentation.common.helpers import default_on_start_handler

from . import states
from .common import (
    goods_card_photo,
    goods_card_txt,
    photo_getter,
)


@inject
async def on_confirmation_delete(
    _: CallbackQuery,
    __: Button,
    manager: DialogManager,
    action: FromDishka[DeleteGoods],
) -> None:
    await action(DeleteGoodsInputData(manager.dialog_data.get("goods_id")))


async def on_start_btn_edit_dialog(
    _: CallbackQuery, __: Button, manager: DialogManager
) -> None:
    await manager.start(
        state=states.EditGoods.START,
        data={"goods_id": manager.dialog_data["goods_id"]},
    )


@inject
async def goods_view_getter(
    action: FromDishka[GetGoods], dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    goods_id = dialog_manager.dialog_data["goods_id"]

    goods = await action(GetGoodsInputData(goods_id))

    title = str(goods.title)
    price = str(goods.price)
    category_type = goods.goods_type
    category = ACTUAL_GOODS_TYPES[category_type]
    path = goods.metadata_path

    dialog_manager.dialog_data["goods_id"] = goods_id
    dialog_manager.dialog_data["title"] = title
    dialog_manager.dialog_data["price"] = price
    dialog_manager.dialog_data["category_type"] = category_type
    dialog_manager.dialog_data["category"] = category
    dialog_manager.dialog_data["path"] = path

    return dialog_manager.dialog_data


view_goods_dialog = Dialog(
    Window(
        goods_card_photo,
        goods_card_txt,
        Button(
            Const("✏️ Редагувати"),
            id="edit_goods_menu",
            on_click=on_start_btn_edit_dialog,
        ),
        Next(Const("🗑 Видалити")),
        Cancel(Const(BACK_BTN_TXT)),
        state=states.ViewGoods.VIEW,
        getter=photo_getter,
    ),
    Window(
        goods_card_photo,
        Multi(
            goods_card_txt,
            Const("Підтвердіть видалення товару 👇"),
            sep="\n\n",
        ),
        Row(
            Cancel(
                Const("Так"),
                on_click=on_confirmation_delete,  # noqa: ignore
            ),
            Back(Const("Ні")),
        ),
        state=states.ViewGoods.DELETE,
    ),
    on_start=default_on_start_handler,
    getter=goods_view_getter,
)

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
from presentation.common.consts import BACK_BTN_TXT
from presentation.common.getters.goods import (
    goods_card_photo,
    goods_card_txt,
    goods_view_getter,
    photo_getter,
)
from presentation.common.helpers import default_on_start_handler

from . import states


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

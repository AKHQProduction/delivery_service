from typing import Any

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, Start
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.interfaces.filters import Pagination
from application.goods.gateway import GoodsFilters
from application.goods.interactors.get_many_goods_by_admin import (
    GetManyGoodsByAdmin,
    GetManyGoodsByAdminInputData,
)
from entities.goods.models import GoodsId
from presentation.admin.handlers.admin.goods import states
from presentation.common.consts import GOODS_BTN_TEXT

router = Router()


@router.message(Command("goods"))
@router.message(F.text == GOODS_BTN_TEXT)
async def goods_workflow_btn(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.GoodsWorkflow.MAIN_MENU,
        mode=StartMode.RESET_STACK,
    )


@inject
async def get_all_goods_by_admin(
    action: FromDishka[GetManyGoodsByAdmin], **_kwargs
) -> dict[str, Any]:
    output_data = await action(
        GetManyGoodsByAdminInputData(
            pagination=Pagination(), filters=GoodsFilters()
        )
    )

    return {"total": output_data.total, "goods": output_data.goods}


async def on_goods_selected(
    _: CallbackQuery, __: Button, manager: DialogManager, value: GoodsId
) -> None:
    await manager.start(state=states.ViewGoods.VIEW, data={"goods_id": value})


goods_workflow_dialog = Dialog(
    Window(
        Format("У вас всього {total} товарів"),
        Start(
            id="add_new_goods",
            text=Const("➕ Додати товар"),
            state=states.AddNewGoods.TITLE,
        ),
        ScrollingGroup(
            Select(
                id="select_goods",
                items="goods",
                text=Format("{item.title} | {item.price} UAH"),
                item_id_getter=lambda item: item.goods_id,
                type_factory=lambda item: GoodsId(item),
                on_click=on_goods_selected,
            ),
            id="all_goods_admin_view",
            hide_on_single_page=True,
            width=2,
            height=10,
            when=F["total"] > 0,
        ),
        state=states.GoodsWorkflow.MAIN_MENU,
        getter=get_all_goods_by_admin,
    ),
)

import operator
from decimal import Decimal
from typing import Any

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.kbd import (
    Back,
    Button,
    Counter,
    ManagedCounter,
    Next,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.input_data import Pagination
from application.goods.gateway import GoodsFilters
from application.goods.interactors.get_many_goods import (
    GetManyGoods,
    GetManyGoodsInputData,
)
from entities.goods.models import GoodsId, GoodsType
from presentation.common.consts import (
    ACTUAL_GOODS_TYPES,
    BACK_BTN_TXT,
    CREATE_ORDER_BTN_TXT,
)
from presentation.common.getters.goods import (
    get_goods_types,
    goods_card_photo,
    goods_card_txt,
    goods_view_getter,
    photo_getter,
)

from . import states
from .common import cart_getter, order_items_list

router = Router()


@router.message(F.text == CREATE_ORDER_BTN_TXT)
async def create_order_btn(_msg: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=states.Cart.GOODS_CATEGORY, mode=StartMode.RESET_STACK
    )


async def on_select_goods_type(
    _call: CallbackQuery,
    _widget: Select,
    manager: DialogManager,
    selected: GoodsType,
) -> None:
    manager.dialog_data["goods_type"] = selected
    manager.dialog_data["goods_type_txt"] = ACTUAL_GOODS_TYPES[selected]

    await manager.next()


@inject
async def load_goods_by_select_type(
    action: FromDishka[GetManyGoods], dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    shop_id: int = dialog_manager.middleware_data["shop_id"]
    goods_type = dialog_manager.dialog_data["goods_type"]

    output_data = await action(
        GetManyGoodsInputData(
            pagination=Pagination(),
            filters=GoodsFilters(shop_id=shop_id, goods_type=goods_type),
        )
    )

    return {"goods": output_data.goods, "total": output_data.total}


async def on_select_goods(
    _call: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
    selected: GoodsId,
):
    manager.dialog_data["goods_id"] = selected
    await manager.next()


async def on_value_change(
    _call: CallbackQuery, _widget: ManagedCounter, manager: DialogManager
) -> None:
    manager.dialog_data["is_not_empty_quantity"] = _widget.get_value() > 0


async def on_back_from_state(
    _call: CallbackQuery, _widget: Button, manager: DialogManager
) -> None:
    counter: ManagedCounter = manager.find("goods_item_counter")
    await counter.set_value(0)


async def add_goods_to_card(
    _call: CallbackQuery, _widget: Button, manager: DialogManager
) -> None:
    counter: ManagedCounter = manager.find("goods_item_counter")
    quantity: int = int(counter.get_value())
    goods_id = manager.dialog_data["goods_id"]
    price = Decimal(manager.dialog_data["price"])
    title = manager.dialog_data["title"]

    total_price = quantity * price

    cart = manager.dialog_data.get("cart", {})

    if manager.dialog_data.get("is_edit_mode", False):
        cart[goods_id]["quantity"] = quantity
        cart[goods_id]["total_price"] = str(total_price)
        cart[goods_id]["price_per_item"] = str(price)
    elif goods_id in cart:
        cart[goods_id]["quantity"] += quantity
        cart[goods_id]["total_price"] += str(total_price)
    else:
        cart[goods_id] = {
            "goods_id": goods_id,
            "quantity": quantity,
            "title": title,
            "total_price": str(total_price),
            "price_per_item": str(price),
        }

    manager.dialog_data["cart"] = cart
    manager.dialog_data["is_edit_mode"] = False

    await counter.set_value(0)


async def cart_clear_btn(
    _call: CallbackQuery, _widget: Button, manager: DialogManager
):
    manager.dialog_data.pop("cart")


async def on_select_goods_to_edit(
    _call: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
    selected: GoodsId,
):
    manager.dialog_data["goods_id"] = selected
    manager.dialog_data["is_edit_mode"] = True

    quantity = manager.dialog_data["cart"][selected]["quantity"]

    counter: ManagedCounter = manager.find("goods_item_counter")
    await counter.set_value(quantity)

    await manager.switch_to(state=states.Cart.GOODS_VIEW)


async def on_delete_order_item(
    _call: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
):
    counter: ManagedCounter = manager.find("goods_item_counter")
    goods_id = manager.dialog_data["goods_id"]

    await counter.set_value(0)

    cart: dict[str, Any] = manager.dialog_data["cart"]
    cart.pop(goods_id)

    manager.dialog_data["is_edit_mode"] = False

    if len(cart) > 0:
        await manager.switch_to(state=states.Cart.CART)
    else:
        await manager.switch_to(state=states.Cart.GOODS_CATEGORY)


async def switch_to_create_order_dialog(
    _call: CallbackQuery,
    _widget: Button,
    manager: DialogManager,
):
    cart: dict[str, Any] = manager.dialog_data["cart"]

    await manager.start(state=states.CreateOrder.DATE, data={"cart": cart})


select_goods_dialog = Dialog(
    Window(
        Const("🧺 <b>Ваше замовлення</b>"),
        order_items_list,
        Format(
            "💳 <b>До оплати:</b> {total_cart_price} UAH",
        ),
        SwitchTo(
            Const("🛒 Обрати ще"),
            id="add_new_item_to_cart",
            state=states.Cart.GOODS_CATEGORY,
        ),
        Row(
            Next(Const("✏️ Редагувати корзину")),
            SwitchTo(
                Const("🧹 Очистити корзину"),
                id="cart_clear",
                state=states.Cart.GOODS_CATEGORY,
                on_click=cart_clear_btn,
            ),
        ),
        Button(
            Const("🛍 Сформувати замовлення"),
            id="start_create_order",
            on_click=switch_to_create_order_dialog,
        ),
        getter=cart_getter,
        state=states.Cart.CART,
    ),
    Window(
        Const("Виберіть позицію, яку потрібно редагувати"),
        ScrollingGroup(
            Select(
                text=Format(
                    "{item[title]} | {item[quantity]} одн. | "
                    "{item[total_price]} UAH"
                ),
                id="order_items_slt",
                items="order_items",
                item_id_getter=lambda x: x["goods_id"],
                type_factory=lambda x: GoodsId(x),
                on_click=on_select_goods_to_edit,
            ),
            id="scrolling_order_items",
            width=2,
            height=10,
            hide_on_single_page=True,
        ),
        Back(Const(BACK_BTN_TXT), when=F["dialog_data"]["cart"]),
        getter=cart_getter,
        state=states.Cart.EDIT_CART,
    ),
    Window(
        Multi(Const("Виберіть категорію товара"), sep="\n\n"),
        Select(
            id="select_goods_type",
            text=Format("{item[1]}"),
            items="types",
            item_id_getter=operator.itemgetter(0),
            type_factory=lambda item: GoodsType(item),
            on_click=on_select_goods_type,
        ),
        SwitchTo(
            id="back_to_card",
            text=Const(BACK_BTN_TXT),
            when=F["dialog_data"]["cart"],
            state=states.Cart.CART,
        ),
        getter=get_goods_types,
        state=states.Cart.GOODS_CATEGORY,
    ),
    Window(
        Format("<b>Категорія:</b> {dialog_data[goods_type_txt]} \n"),
        Format("<b>Всього товарів:</b> {total}"),
        ScrollingGroup(
            Select(
                id="current_goods",
                items="goods",
                text=Format("{item.title} | {item.price} UAH"),
                item_id_getter=lambda item: item.goods_id,
                type_factory=lambda item: GoodsId(item),
                on_click=on_select_goods,
            ),
            id="all_goods_client_view",
            hide_on_single_page=True,
            width=2,
            height=10,
            when=F["total"] > 0,
        ),
        Back(Const(BACK_BTN_TXT)),
        getter=load_goods_by_select_type,
        state=states.Cart.GOODS_LIST,
    ),
    Window(
        goods_card_photo,
        Multi(goods_card_txt, Const("Вкажіть кількість товару"), sep="\n\n"),
        SwitchTo(
            id="add_goods_to_cart",
            text=Const("➕ Додати в корзину"),
            state=states.Cart.CART,
            on_click=add_goods_to_card,
            when=F["is_not_empty_quantity"] & ~F["is_edit_mode"],
        ),
        SwitchTo(
            id="edit_goods_in_cart",
            text=Const("🔄 Оновити кількість"),
            state=states.Cart.CART,
            on_click=add_goods_to_card,
            when=F["is_not_empty_quantity"] & F["is_edit_mode"],
        ),
        Counter(id="goods_item_counter", on_value_changed=on_value_change),
        Button(
            text=Const("🗑 Видалити позицію"),
            id="delete_order_item",
            on_click=on_delete_order_item,
            when=F["is_edit_mode"],
        ),
        Back(
            Const(BACK_BTN_TXT),
            on_click=on_back_from_state,
            id="back_to_goods_list",
            when=~F["is_edit_mode"],
        ),
        SwitchTo(
            Const(BACK_BTN_TXT),
            on_click=on_back_from_state,
            id="back_to_edit_cart",
            when=F["is_edit_mode"],
            state=states.Cart.EDIT_CART,
        ),
        getter=[goods_view_getter, photo_getter],
        state=states.Cart.GOODS_VIEW,
    ),
)

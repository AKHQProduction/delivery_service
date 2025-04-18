from typing import Any

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Row,
    ScrollingGroup,
    Select,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.domain.products.product import ProductType
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.infrastructure.integration.telegram.const import (
    ORDERS_BTN,
)
from delivery_service.presentation.bot.widgets.calendar import CustomCalendar
from delivery_service.presentation.bot.widgets.kbd import get_back_btn

from .getters import (
    get_all_shop_products,
    get_product_categories,
    get_product_id,
    get_shop_product,
)
from .kbd import get_product_category_select, get_shop_products_scrolling_group
from .states import OrderMenu

ORDERS_ROUTER = Router()


@ORDERS_ROUTER.message(F.text == ORDERS_BTN)
async def launch_orders_dialog(_: Message, dialog_manager: DialogManager):
    await dialog_manager.start(
        state=OrderMenu.MAIN, mode=StartMode.RESET_STACK
    )


PRODUCT_TYPE_TO_TEXT = {
    ProductType.WATER: "💧 Вода",
    ProductType.ACCESSORIES: "💎 Аксесуари",
}

CURRENT_CART = "current_cart"


async def get_order_cart(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    cart_items = []
    total_cart_price = 0

    cart: dict[str, dict[str, Any]] | None = dialog_manager.dialog_data.get(
        CURRENT_CART
    )
    if cart:
        for value in cart.values():
            total_price = int(value["quantity"]) * FixedDecimal(value["price"])
            total_cart_price += total_price
            value.update({"total_price": str(total_price)})
            cart_items.append(value)

    return {"cart_items": cart_items, "total_cart_price": total_cart_price}


async def get_cart_items(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, list[dict[str, Any]]]:
    cart: dict[str, dict[str, Any]] | None = dialog_manager.dialog_data.get(
        CURRENT_CART
    )

    cart_items = []
    if cart:
        for key, value in cart.items():
            value.update({"id": key})
            cart_items.append(value)

    return {"items": cart_items}


async def get_cart_item(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    item_to_edit = dialog_manager.dialog_data.get("item_to_edit")
    if not item_to_edit:
        raise ValueError()
    cart: dict[str, dict[str, Any]] | None = dialog_manager.dialog_data.get(
        CURRENT_CART
    )
    if not cart:
        raise ValueError()

    item: dict[str, Any] = cart.get(item_to_edit)
    if not item:
        raise ValueError()

    dialog_manager.dialog_data["item_title"] = item["title"]
    return {"title": item["title"], "quantity": item["quantity"]}


async def get_selected_product_category(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    product_type: str | None = dialog_manager.dialog_data.get("product_type")
    if not product_type:
        raise ValueError()

    return {"category_name": PRODUCT_TYPE_TO_TEXT[ProductType(product_type)]}


async def on_select_product_item(
    call: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    cart: dict[str, Any] | None = manager.dialog_data.get(CURRENT_CART)
    if cart and cart.get(value) and call.message:
        await call.message.answer("❌ Товар вже є в корзині")
        return await manager.switch_to(
            state=OrderMenu.CART, show_mode=ShowMode.SEND
        )

    manager.dialog_data["product_id"] = value
    return await manager.switch_to(state=OrderMenu.PRODUCT_COUNTER)


async def on_select_product_category(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["product_type"] = value
    await manager.switch_to(state=OrderMenu.PRODUCTS_CATALOG)


async def on_select_item_to_edit(
    _: CallbackQuery, __: Widget, manager: DialogManager, vale: str
) -> None:
    manager.dialog_data["item_to_edit"] = vale
    await manager.switch_to(state=OrderMenu.ITEM_EDITING_MENU)


@inject
async def on_find_customer_by_phone(
    msg: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
    customer_reader: FromDishka[CustomerGateway],
) -> Message | None:
    customer = await customer_reader.read_with_phone(value)
    if not customer:
        return await msg.answer("❌ Не вдалось знайти користувача")

    manager.dialog_data["customer_id"] = str(customer.customer_id)
    manager.dialog_data["full_name"] = customer.full_name

    return await manager.next()


async def on_input_product_quantity(
    msg: Message, __: ManagedTextInput, manager: DialogManager, value: int
) -> Message | None:
    if value <= 0 and msg:
        return await msg.answer("❌ Кількість повинна бути більша за 0")

    product_id = get_product_id(manager)
    product_title = manager.dialog_data.get("product_title")
    product_price = manager.dialog_data.get("product_price")
    if not product_title or not product_price:
        raise ValueError()

    current_cart: dict[str, Any] | None = manager.dialog_data.get(
        "current_cart"
    )
    if not current_cart:
        manager.dialog_data.update(
            {
                "current_cart": {
                    str(product_id): {
                        "title": product_title,
                        "price": product_price,
                        "quantity": value,
                    }
                }
            }
        )
    else:
        current_cart.update(
            {
                str(product_id): {
                    "title": product_title,
                    "price": product_price,
                    "quantity": value,
                }
            }
        )

    if msg:
        await msg.answer("✅ Товар додано до корзини")
    return await manager.switch_to(OrderMenu.CART, show_mode=ShowMode.SEND)


async def on_input_edit_product_quantity(
    msg: Message, __: ManagedTextInput, manager: DialogManager, value: int
) -> Message | None:
    if value <= 0 and msg:
        return await msg.answer("❌ Кількість повинна бути більша за 0")

    item_to_edit: str | None = manager.dialog_data.get("item_to_edit")
    cart: dict[str, dict[str, Any]] | None = manager.dialog_data.get(
        CURRENT_CART
    )

    if not item_to_edit or not cart:
        raise ValueError()

    item_to_editing = cart.get(item_to_edit)
    if not item_to_editing:
        raise ValueError()

    item_to_editing["quantity"] = value
    return await manager.switch_to(state=OrderMenu.CART)


async def clear_cart(
    _: CallbackQuery, __: Widget, manager: DialogManager
) -> None:
    cart = manager.dialog_data.get(CURRENT_CART)
    if cart:
        manager.dialog_data.pop(CURRENT_CART)


async def on_delete_cart_item(
    _: CallbackQuery, __: Widget, manager: DialogManager
) -> None:
    item_to_edit: str | None = manager.dialog_data.get("item_to_edit")
    cart: dict[str, dict[str, Any]] | None = manager.dialog_data.get(
        CURRENT_CART
    )

    if not item_to_edit or not cart:
        raise ValueError()

    item_to_delete = cart.get(item_to_edit)
    if not item_to_delete:
        raise ValueError()

    cart.pop(item_to_edit)
    await manager.switch_to(state=OrderMenu.CART)


ORDERS_DIALOG = Dialog(
    Window(
        Const("🚚 <b>Меню замовлень</b>"),
        SwitchTo(
            text=Const("➕ Створити замовлення"),
            state=OrderMenu.FIND_CUSTOMER,
            id="add_new_product",
        ),
        state=OrderMenu.MAIN,
    ),
    Window(
        Const("Вкажіть контактний номер телефона клієнта"),
        Const("<i>В форматі +380</i>"),
        TextInput(
            id="find_customer_by_phone", on_success=on_find_customer_by_phone
        ),
        get_back_btn(state=OrderMenu.MAIN),
        state=OrderMenu.FIND_CUSTOMER,
    ),
    Window(
        Format("Створити замовлення для {dialog_data[full_name]}?"),
        SwitchTo(
            text=Const("✅ Підтвердити"),
            id="accept_customer_for_order",
            state=OrderMenu.CART,
        ),
        get_back_btn(btn_text="❌ Відмінити", state=OrderMenu.MAIN),
        state=OrderMenu.CUSTOMER_CONFIRMATION,
    ),
    Window(
        Const("<b>🧺 Поточне замовлення</b>\n"),
        Jinja(
            "<blockquote expandable>"
            "{% for item in cart_items %}"
            "• <b>{{item.title}}</b>: {{item.quantity}} * {{item.price}} "
            "<b>UAH</b> ~ {{item.total_price}} <b>UAH</b>\n"
            "{% endfor %}"
            "</blockquote>"
        ),
        Format("<b>Всього до сплати:</b> {total_cart_price} <b>UAH</b>"),
        SwitchTo(
            id="add_product_to_cart",
            state=OrderMenu.PRODUCTS_CATEGORY,
            text=Const("➕ Додати товар"),
        ),
        Row(
            SwitchTo(
                id="to_editing_menu",
                state=OrderMenu.EDITING_MENU,
                text=Const("✍️ Редагувати"),
            ),
            SwitchTo(
                id="continue",
                state=OrderMenu.SELECT_DATE,
                text=Const("➡️ Далі"),
            ),
            when=F["cart_items"],
        ),
        get_back_btn(state=OrderMenu.FIND_CUSTOMER, on_click=clear_cart),
        getter=get_order_cart,
        state=OrderMenu.CART,
    ),
    Window(
        Const("<b>Категорії товарів</b>"),
        get_product_category_select(on_click=on_select_product_category),
        get_back_btn(state=OrderMenu.CART),
        getter=get_product_categories,
        state=OrderMenu.PRODUCTS_CATEGORY,
    ),
    Window(
        Format("<b>Обрана категорія:</b> {category_name}"),
        Format("<b>Всього товарі:</b> {total}"),
        get_shop_products_scrolling_group(on_click=on_select_product_item),
        get_back_btn(state=OrderMenu.PRODUCTS_CATEGORY),
        getter=[get_all_shop_products, get_selected_product_category],
        state=OrderMenu.PRODUCTS_CATALOG,
    ),
    Window(
        Format("Вкажіть кількість товару {title}"),
        TextInput(
            id="quantity_input",
            type_factory=int,
            on_success=on_input_product_quantity,
        ),
        get_back_btn(state=OrderMenu.PRODUCTS_CATALOG),
        getter=get_shop_product,
        state=OrderMenu.PRODUCT_COUNTER,
    ),
    Window(
        Const("Оберіть позицію для редагування"),
        ScrollingGroup(
            Select(
                id="cart_item",
                items="items",
                item_id_getter=lambda item: item["id"],
                text=Format("{item[title]}"),
                on_click=on_select_item_to_edit,
            ),
            id="cart_items",
            width=2,
            height=10,
            hide_on_single_page=True,
        ),
        get_back_btn(state=OrderMenu.CART),
        getter=get_cart_items,
        state=OrderMenu.EDITING_MENU,
    ),
    Window(
        Format(
            "<b>Назва позиції:</b> {title}\n" "<b>Кількість:</b> {quantity}"
        ),
        Row(
            SwitchTo(
                id="edit_quantity",
                text=Const("✍️ Редагувати кількість"),
                state=OrderMenu.EDIT_QUANTITY,
            ),
            Button(
                id="delete_order_item",
                text=Const("🗑 Видалити"),
                on_click=on_delete_cart_item,
            ),
        ),
        get_back_btn(state=OrderMenu.EDITING_MENU),
        getter=get_cart_item,
        state=OrderMenu.ITEM_EDITING_MENU,
    ),
    Window(
        Format("Вкажіть нову кількість товару {dialog_data[item_title]}"),
        TextInput(
            id="edit_quantity_input",
            type_factory=int,
            on_success=on_input_edit_product_quantity,
        ),
        get_back_btn(state=OrderMenu.ITEM_EDITING_MENU),
        state=OrderMenu.EDIT_QUANTITY,
    ),
    Window(
        Const("Оберіть дату доставки\n"),
        Const("<i>🟥 - вихідний день</i>"),
        CustomCalendar(id="delivery_calendar"),
        get_back_btn(state=OrderMenu.CART),
        state=OrderMenu.SELECT_DATE,
    ),
)

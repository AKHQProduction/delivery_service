import operator
from datetime import date, datetime
from typing import Any
from uuid import UUID

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (
    ChatEvent,
    Dialog,
    DialogManager,
    ShowMode,
    StartMode,
    Window,
)
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    ManagedCalendar,
    Row,
    ScrollingGroup,
    Select,
    Start,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja, Multi
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from zoneinfo import ZoneInfo

from delivery_service.application.commands.delete_order import (
    DeleteOrderRequest,
)
from delivery_service.application.commands.make_new_order import (
    MakeNewOrderRequest,
)
from delivery_service.application.query.order import (
    GetAllShopOrdersRequest,
    GetShopOrderRequest,
)
from delivery_service.application.query.ports.address_gateway import (
    AddressGateway,
    AddressGatewayFilters,
)
from delivery_service.application.query.ports.customer_gateway import (
    CustomerGateway,
)
from delivery_service.application.query.shop import GetShopRequest
from delivery_service.domain.addresses.address_id import AddressID
from delivery_service.domain.orders.order import DeliveryPreference
from delivery_service.domain.products.product import ProductID, ProductType
from delivery_service.domain.shared.dto import OrderLineData
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.infrastructure.integration.telegram.const import (
    ORDERS_BTN,
)
from delivery_service.presentation.bot.widgets.calendar import (
    ShopAvailabilityCalendar,
    is_day_off,
)
from delivery_service.presentation.bot.widgets.kbd import get_back_btn

from .getters import (
    get_all_shop_products,
    get_customer_id,
    get_order_id,
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

DELIVERY_PREFERENCE_TO_TEXT = {
    DeliveryPreference.MORNING: "Перша половина дня",
    DeliveryPreference.AFTERNOON: "Друга половина дня",
}

CURRENT_CART = "current_cart"


@inject
async def get_orders(sender: FromDishka[Sender], **_kwargs) -> dict[str, Any]:
    response = await sender.send(GetAllShopOrdersRequest())

    return {"total": response.total, "orders": response.orders}


@inject
async def get_order(
    sender: FromDishka[Sender], dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    order_id = get_order_id(dialog_manager)

    order = await sender.send(GetShopOrderRequest(order_id=order_id))

    return {
        "order_lines": order.order_lines,
        "full_name": order.customer_full_name,
        "delivery_date": order.delivery_date,
        "delivery_preference": DELIVERY_PREFERENCE_TO_TEXT[
            order.delivery_preference
        ],
        "total_order_price": order.total_order_price,
    }


@inject
async def get_customer_addresses(
    dialog_manager: DialogManager, reader: FromDishka[AddressGateway], **kwargs
) -> dict[str, Any]:
    customer_id = get_customer_id(dialog_manager)
    filters = AddressGatewayFilters(user_id=customer_id)

    return {
        "addresses": await reader.read_many(filters),
        "total": await reader.total(filters),
    }


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


@inject
async def get_shop_data(
    dialog_manager: DialogManager, sender: FromDishka[Sender], **_kwargs
) -> dict[str, Any]:
    shop_data = await sender.send(GetShopRequest())

    dialog_manager.dialog_data["regular_days_off"] = shop_data.regular_days_off
    dialog_manager.dialog_data["irregular_days_off"] = (
        shop_data.irregular_days_off
    )

    return {}


async def get_selected_product_category(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    product_type: str | None = dialog_manager.dialog_data.get("product_type")
    if not product_type:
        raise ValueError()

    return {"category_name": PRODUCT_TYPE_TO_TEXT[ProductType(product_type)]}


async def get_delivery_preferences(**_kwargs) -> dict[str, Any]:
    preferences = []
    for key, value in DELIVERY_PREFERENCE_TO_TEXT.items():
        preferences.append((value, key.value))

    return {"delivery_preferences": preferences}


async def get_all_order_data_to_preview(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    data = dialog_manager.dialog_data

    return {
        "full_name": data.get("full_name"),
        "delivery_date": data.get("delivery_date"),
        "delivery_preference": DELIVERY_PREFERENCE_TO_TEXT[
            DeliveryPreference(data.get("delivery_preference"))
        ],
    }


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


async def on_select_delivery_date(
    call: ChatEvent,
    _widget: ManagedCalendar,
    manager: DialogManager,
    clicked_date: date,
) -> bool | None:
    error_text: str = "❌ Доставка в цей день неможлива"
    if is_day_off(clicked_date, manager) and isinstance(call, CallbackQuery):
        return await call.answer(text=error_text, show_alert=True)

    current_date = datetime.now(tz=ZoneInfo("Europe/Kiev")).date()
    if current_date > clicked_date and isinstance(call, CallbackQuery):
        return await call.answer(text=error_text, show_alert=True)

    manager.dialog_data["delivery_date"] = clicked_date.strftime("%d.%m.%Y")
    return await manager.switch_to(state=OrderMenu.SELECT_DELIVERY_PREFERENCE)


async def on_select_delivery_preference(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["delivery_preference"] = value
    await manager.switch_to(state=OrderMenu.PREVIEW)


async def on_select_order_item(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["order_id"] = value
    await manager.switch_to(state=OrderMenu.ORDER_CARD)


async def on_select_address_item(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["address_id"] = value
    await manager.switch_to(state=OrderMenu.CART)


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


@inject
async def on_delete_order(
    _: CallbackQuery,
    __: Widget,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    order_id = get_order_id(manager)
    await sender.send(DeleteOrderRequest(order_id))

    await manager.switch_to(state=OrderMenu.MAIN)


@inject
async def on_confirm_order_creation(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    data = manager.dialog_data

    customer_id = get_customer_id(manager)

    address_id_str = data.get("address_id")
    address_id = AddressID(UUID(address_id_str)) if address_id_str else None

    delivery_date_str = data.get("delivery_date")
    delivery_date = (
        datetime.strptime(delivery_date_str, "%d.%m.%Y").date()  # noqa: DTZ007
        if delivery_date_str
        else None
    )

    delivery_preference = DeliveryPreference(data.get("delivery_preference"))

    cart: dict[str, dict[str, Any]] | None = manager.dialog_data.get(
        CURRENT_CART
    )

    if (
        not address_id
        or not delivery_date
        or not delivery_preference
        or not cart
    ):
        raise ValueError()

    order_lines = []
    for key, value in cart.items():
        order_lines.append(
            OrderLineData(
                product_id=ProductID(UUID(key)),
                title=value["title"],
                price_per_item=FixedDecimal(value["price"]),
                quantity=value["quantity"],
            )
        )

    await sender.send(
        MakeNewOrderRequest(
            customer_id=customer_id,
            delivery_date=delivery_date,
            delivery_preference=delivery_preference,
            order_lines=order_lines,
            address_id=address_id,
        )
    )

    await call.answer("✅ Замовлення створено")
    await manager.start(
        state=OrderMenu.MAIN,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.SEND,
    )


ORDERS_DIALOG = Dialog(
    Window(
        Const("🚚 <b>Меню замовлень</b>"),
        SwitchTo(
            text=Const("➕ Створити замовлення"),
            state=OrderMenu.FIND_CUSTOMER,
            id="add_new_product",
        ),
        ScrollingGroup(
            Select(
                id="order_item",
                items="orders",
                item_id_getter=lambda item: item.order_id,
                text=Format(
                    "{pos}. {item.customer_full_name} | {item.delivery_date}"
                ),
                on_click=on_select_order_item,
            ),
            id="all_shop_orders",
            width=1,
            height=10,
            hide_on_single_page=True,
            when=F["total"] > 0,
        ),
        getter=get_orders,
        state=OrderMenu.MAIN,
    ),
    Window(
        Multi(
            Format(
                "<b>Замовлення для:</b> {full_name}\n"
                "<b>Дата замовлення:</b> {delivery_date}\n"
                "<b>Орієнтовний час доставки:</b> {delivery_preference}"
            ),
            Jinja(
                "<b>Всього до сплати:</b> {{total_order_price}} <b>UAH</b>"
                "<blockquote expandable>"
                "{% for item in order_lines %}"
                "• <b>{{item.title}}</b>: {{item.quantity}} одн.\n"
                "{% endfor %}"
                "</blockquote>"
            ),
            sep="\n\n",
        ),
        SwitchTo(
            text=Const("🗑 Видалить"),
            id="to_order_delete",
            state=OrderMenu.ORDER_DELETE_CONFIRMATION,
        ),
        get_back_btn(state=OrderMenu.MAIN),
        getter=get_order,
        state=OrderMenu.ORDER_CARD,
    ),
    Window(
        Format("Видалить замовлення?"),
        SwitchTo(
            text=Const("✅ Підтвердити"),
            id="accept_order_deleting",
            state=OrderMenu.MAIN,
            on_click=on_delete_order,
        ),
        get_back_btn(btn_text="❌ Відмінити", state=OrderMenu.ORDER_CARD),
        getter=get_order,
        state=OrderMenu.ORDER_DELETE_CONFIRMATION,
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
        Format("Оберіть адресу {dialog_data[full_name]} для замовлення"),
        ScrollingGroup(
            Select(
                id="address",
                items="addresses",
                item_id_getter=lambda item: item.address_id,
                text=Format(
                    "{pos}. {item.city}, {item.street} {item.house_number}"
                ),
                on_click=on_select_address_item,
            ),
            id="all_customer_addresses",
            width=1,
            height=10,
            hide_on_single_page=True,
            when=F["total"] > 0,
        ),
        get_back_btn(state=OrderMenu.MAIN),
        getter=get_customer_addresses,
        state=OrderMenu.SELECT_ADDRESS,
    ),
    Window(
        Const("<b>🧺 Поточне замовлення</b>\n"),
        Jinja(
            "<blockquote expandable>"
            "{% for item in cart_items %}"
            "• <b>{{item.title}}</b>: {{item.quantity}} одн. * {{item.price}} "
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
        ShopAvailabilityCalendar(
            id="delivery_calendar", on_click=on_select_delivery_date
        ),
        get_back_btn(state=OrderMenu.CART),
        getter=get_shop_data,
        state=OrderMenu.SELECT_DATE,
    ),
    Window(
        Const("Оберіть зручний час доставки"),
        Select(
            Format("{item[0]}"),
            id="s_delivery_preference",
            item_id_getter=operator.itemgetter(1),
            items="delivery_preferences",
            on_click=on_select_delivery_preference,
        ),
        get_back_btn(state=OrderMenu.SELECT_DATE),
        getter=get_delivery_preferences,
        state=OrderMenu.SELECT_DELIVERY_PREFERENCE,
    ),
    Window(
        Multi(
            Const("<b>Перевірте замовлення 👇</b>"),
            Format(
                "<b>Замовлення для:</b> {full_name}\n"
                "<b>Дата замовлення:</b> {delivery_date}\n"
                "<b>Орієнтовний час доставки:</b> {delivery_preference}"
            ),
            Jinja(
                "<b>Всього до сплати:</b> {{total_cart_price}} <b>UAH</b>"
                "<blockquote expandable>"
                "{% for item in cart_items %}"
                "• <b>{{item.title}}</b>: {{item.quantity}} одн.\n"
                "{% endfor %}"
                "</blockquote>"
            ),
            sep="\n\n",
        ),
        Button(
            text=Const("✅ Підтвердити"),
            id="accept_order_creation",
            on_click=on_confirm_order_creation,
        ),
        Start(
            text=Const("❌ Відмінити"),
            state=OrderMenu.MAIN,
            id="restart_order_dialog",
            mode=StartMode.RESET_STACK,
        ),
        getter=[get_all_order_data_to_preview, get_order_cart],
        state=OrderMenu.PREVIEW,
    ),
)

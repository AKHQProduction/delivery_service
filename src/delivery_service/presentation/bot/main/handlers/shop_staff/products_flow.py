from decimal import InvalidOperation
from typing import Any

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Row,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Case, Const, Format, Multi
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.commands.add_new_product import (
    AddNewProductRequest,
)
from delivery_service.application.commands.delete_product import (
    DeleteProductRequest,
)
from delivery_service.application.commands.edit_product import (
    EditProductPriceRequest,
    EditProductTitleRequest,
)
from delivery_service.domain.products.errors import ProductAlreadyExistsError
from delivery_service.domain.products.product import ProductType
from delivery_service.domain.shared.new_types import FixedDecimal
from delivery_service.infrastructure.integration.telegram.const import (
    PRODUCTS_BTN,
)
from delivery_service.presentation.bot.widgets.kbd import get_back_btn

from . import states
from .getters import (
    get_all_shop_products,
    get_product_categories,
    get_product_id,
    get_shop_product,
)
from .kbd import get_product_category_select, get_shop_products_scrolling_group

PRODUCTS_ROUTER = Router()


@PRODUCTS_ROUTER.message(F.text == PRODUCTS_BTN)
async def launch_product_menu(
    _: Message, dialog_manager: DialogManager
) -> None:
    await dialog_manager.start(
        state=states.ProductMenu.MAIN, mode=StartMode.RESET_STACK
    )


async def get_edited_shop_product(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    return {"is_edited": dialog_manager.dialog_data.get("is_edited", False)}


async def get_new_product_data(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    title = dialog_manager.dialog_data.get("new_product_name")
    price = dialog_manager.dialog_data.get("new_product_price")
    product_type = dialog_manager.dialog_data.get("new_product_type")

    return {
        "title": title,
        "price": price,
        "product_type": ProductType(product_type),
    }


async def on_select_product_item(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["product_id"] = value
    await manager.switch_to(state=states.ProductMenu.PRODUCT_CARD)


async def on_select_product_type(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["new_product_type"] = value
    await manager.next()


async def on_input_product_title(
    _: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["new_product_name"] = value
    await manager.next()


@inject
async def on_input_edited_product_title(
    _: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
    sender: FromDishka[Sender],
) -> None:
    product_id = get_product_id(manager)

    await sender.send(
        EditProductTitleRequest(product_id=product_id, new_title=value)
    )

    await manager.switch_to(state=states.ProductMenu.EDIT_MENU)


async def on_input_product_price(
    msg: Message, __: ManagedTextInput, manager: DialogManager, value: str
) -> Message | None:
    try:
        FixedDecimal(value)
    except (InvalidOperation, ValueError):
        return await msg.answer("Ви ввели некорректний тип ціни")

    manager.dialog_data["new_product_price"] = value
    return await manager.next()


@inject
async def on_input_edited_product_price(
    msg: Message,
    __: ManagedTextInput,
    manager: DialogManager,
    value: str,
    sender: FromDishka[Sender],
) -> Message | None:
    try:
        new_price = FixedDecimal(value)
    except (InvalidOperation, ValueError):
        return await msg.answer("Ви ввели некорректний тип ціни")

    product_id = get_product_id(manager)

    await sender.send(
        EditProductPriceRequest(product_id=product_id, new_price=new_price)
    )

    return await manager.switch_to(state=states.ProductMenu.EDIT_MENU)


@inject
async def on_accept_product_creation(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    title = manager.dialog_data.get("new_product_name")
    price = manager.dialog_data.get("new_product_price")
    product_type = manager.dialog_data.get("new_product_type")

    if not title or not price or not product_type:
        raise ValueError()

    try:
        await sender.send(
            AddNewProductRequest(
                title=title,
                price=FixedDecimal(price),
                product_type=ProductType(product_type),
            )
        )

    except ProductAlreadyExistsError:
        if call.message:
            await call.message.answer("Вже є товар з таким ім'ям‼️")
        return await manager.switch_to(
            state=states.ProductMenu.PRODUCT_TITLE, show_mode=ShowMode.SEND
        )

    if call.message:
        await call.message.answer("✅️ Товар успішно додано")
    return await manager.switch_to(
        state=states.ProductMenu.MAIN, show_mode=ShowMode.SEND
    )


@inject
async def on_accept_product_delete(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    product_id = get_product_id(manager)

    await sender.send(DeleteProductRequest(product_id=product_id))

    if call.message:
        await call.message.answer("✅️ Товар успішно видалено")
    await manager.switch_to(
        state=states.ProductMenu.MAIN, show_mode=ShowMode.SEND
    )


PRODUCT_CARD = Multi(
    Format(
        "<b>Назва:</b> {title}\n" "<b>Ціна:</b> {price}\n" "<b>Категорія:</b> "
    )
    + Case(
        texts={
            ProductType.WATER: Const("Вода"),
            ProductType.ACCESSORIES: Const("Інше"),
        },
        selector=F["product_type"],
    )
)

PRODUCTS_DIALOG = Dialog(
    Window(
        Const("📦 <b>Меню товарів</b>"),
        SwitchTo(
            text=Const("➕ Додать товар"),
            state=states.ProductMenu.PRODUCT_TITLE,
            id="add_new_product",
        ),
        get_shop_products_scrolling_group(on_click=on_select_product_item),
        getter=get_all_shop_products,
        state=states.ProductMenu.MAIN,
    ),
    Window(
        PRODUCT_CARD,
        Row(
            SwitchTo(
                id="edit_product",
                text=Const("✏️ Редагувати"),
                state=states.ProductMenu.EDIT_MENU,
            ),
            SwitchTo(
                id="delete_product",
                text=Const("🗑 Видалить"),
                state=states.ProductMenu.DELETE_CONFIRMATION,
            ),
        ),
        get_back_btn(state=states.ProductMenu.MAIN),
        getter=get_shop_product,
        state=states.ProductMenu.PRODUCT_CARD,
    ),
    Window(
        Const("1️⃣ Вкажіть ім'я товару"),
        TextInput(id="input_product_name", on_success=on_input_product_title),
        get_back_btn(state=states.ProductMenu.MAIN),
        state=states.ProductMenu.PRODUCT_TITLE,
    ),
    Window(
        Const("2️⃣ Вкажіть ціну товару"),
        TextInput(id="input_product_price", on_success=on_input_product_price),
        get_back_btn(state=states.ProductMenu.PRODUCT_TITLE),
        state=states.ProductMenu.PRODUCT_PRICE,
    ),
    Window(
        Const("3️⃣ Вкажіть тип продукта"),
        get_product_category_select(on_select_product_type),
        get_back_btn(state=states.ProductMenu.PRODUCT_PRICE),
        getter=get_product_categories,
        state=states.ProductMenu.PRODUCT_TYPE,
    ),
    Window(
        Const("<b>Перевірте карточку товара</b>\n"),
        PRODUCT_CARD,
        Const("<b>Підтвердіть створення товару👇</b>"),
        Button(
            text=Const("✅ Підтвердити"),
            id="accept_product_creation",
            on_click=on_accept_product_creation,
        ),
        get_back_btn(btn_text="❌ Відмінити", state=states.ProductMenu.MAIN),
        getter=get_new_product_data,
        state=states.ProductMenu.PREVIEW,
    ),
    Window(
        Const("<b>Меню редагування товару</b>\n"),
        PRODUCT_CARD,
        Row(
            SwitchTo(
                id="edit_title",
                text=Const("Редагувати ім'я"),
                state=states.ProductMenu.EDIT_PRODUCT_TITLE,
            ),
            SwitchTo(
                id="edit_price",
                text=Const("Редагувати ціну"),
                state=states.ProductMenu.EDIT_PRODUCT_PRICE,
            ),
        ),
        get_back_btn(state=states.ProductMenu.PRODUCT_CARD),
        getter=get_shop_product,
        state=states.ProductMenu.EDIT_MENU,
    ),
    Window(
        Const("Введіть нове ім'я товару"),
        TextInput(
            id="input_edited_product_title",
            on_success=on_input_edited_product_title,
        ),
        get_back_btn(state=states.ProductMenu.EDIT_MENU),
        state=states.ProductMenu.EDIT_PRODUCT_TITLE,
    ),
    Window(
        Const("Введіть нову ціну товару"),
        TextInput(
            id="input_edited_product_price",
            on_success=on_input_edited_product_price,
        ),
        get_back_btn(state=states.ProductMenu.EDIT_MENU),
        state=states.ProductMenu.EDIT_PRODUCT_PRICE,
    ),
    Window(
        Format("Підтвердіть видалення {dialog_data[product_tile]}"),
        Button(
            text=Const("✅ Підтвердити"),
            id="accept_product_delete",
            on_click=on_accept_product_delete,
        ),
        get_back_btn(
            btn_text="❌ Відмінити", state=states.ProductMenu.PRODUCT_CARD
        ),
        state=states.ProductMenu.DELETE_CONFIRMATION,
    ),
)

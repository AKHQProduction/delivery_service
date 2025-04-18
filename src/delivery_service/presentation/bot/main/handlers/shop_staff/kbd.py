import operator

from aiogram import F
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.kbd.select import OnItemClick
from aiogram_dialog.widgets.text import Format


def get_shop_products_scrolling_group(
    on_click: OnItemClick | None = None,
) -> ScrollingGroup:
    return ScrollingGroup(
        Select(
            id="product_item",
            items="products",
            item_id_getter=lambda item: item.product_id,
            text=Format("{pos}. {item.title}"),
            on_click=on_click,
        ),
        id="all_shop_products",
        width=2,
        height=10,
        hide_on_single_page=True,
        when=F["total"] > 0,
    )


def get_product_category_select(on_click: OnItemClick | None = None) -> Select:
    return Select(
        Format("{item[0]}"),
        id="s_product_type",
        item_id_getter=operator.itemgetter(1),
        items="product_types",
        on_click=on_click,
    )

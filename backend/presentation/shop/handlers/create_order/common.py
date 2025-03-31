from decimal import Decimal
from typing import Any

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.text import Jinja

order_items_list = Jinja(
    """
<blockquote expandable>{% for item in order_items %}
{{item.title}} x {{item.quantity}} ~ {{item.total_price}} UAH
{% endfor %}</blockquote>"""
)


async def cart_getter(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any] | None:
    if cart := dialog_manager.dialog_data.get("cart", {}):
        total_cart_price = 0
        for item in cart.values():
            total_cart_price += Decimal(item["total_price"])
        order_items = list(cart.values())

        return {
            "total_cart_price": str(total_cart_price),
            "order_items": order_items,
        }
    return {}

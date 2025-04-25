from typing import Any

from aiogram_dialog import DialogManager
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.query.ports.address_gateway import (
    AddressGateway,
    AddressGatewayFilters,
)
from delivery_service.application.query.ports.product_gateway import (
    ProductGateway,
    ProductGatewayFilters,
)
from delivery_service.application.query.product import GetAllProductsRequest
from delivery_service.domain.orders.order_ids import OrderID
from delivery_service.domain.products.product import ProductID, ProductType
from delivery_service.domain.shared.user_id import UserID


@inject
async def get_all_shop_products(
    sender: FromDishka[Sender], dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any]:
    product_type: str | None = dialog_manager.dialog_data.get("product_type")
    response = await sender.send(
        GetAllProductsRequest(
            filters=ProductGatewayFilters(
                product_type=ProductType(product_type)
                if product_type
                else None
            )
        )
    )

    return {"products": response.products, "total": response.total}


async def get_product_categories(**_kwargs) -> dict[str, Any]:
    return {
        "product_types": [
            ("Вода", ProductType.WATER.value),
            ("Інше", ProductType.ACCESSORIES.value),
        ]
    }


def get_product_id(manager: DialogManager) -> ProductID:
    product_id_str = manager.dialog_data.get("product_id")
    if not product_id_str:
        raise ValueError()

    return ProductID(product_id_str)


def get_order_id(manager: DialogManager) -> OrderID:
    order_id_str = manager.dialog_data.get("order_id")
    if not order_id_str:
        raise ValueError()

    return OrderID(order_id_str)


@inject
async def get_shop_product(
    product_reader: FromDishka[ProductGateway],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    product_id = get_product_id(dialog_manager)
    product = await product_reader.read_with_id(product_id)
    if not product:
        raise ValueError()

    dialog_manager.dialog_data["product_title"] = product.title
    dialog_manager.dialog_data["product_price"] = str(product.price)

    return {
        "title": product.title,
        "price": product.price,
        "product_type": product.product_type,
    }


def get_customer_id(manager: DialogManager) -> UserID:
    customer_id_str = manager.dialog_data.get("customer_id")
    if not customer_id_str:
        raise ValueError()

    return UserID(customer_id_str)


@inject
async def get_customer_addresses(
    dialog_manager: DialogManager,
    reader: FromDishka[AddressGateway],
    **_kwargs,
) -> dict[str, Any]:
    customer_id = get_customer_id(dialog_manager)
    filters = AddressGatewayFilters(user_id=customer_id)

    return {
        "addresses": await reader.read_many(filters),
        "total": await reader.total(filters),
    }

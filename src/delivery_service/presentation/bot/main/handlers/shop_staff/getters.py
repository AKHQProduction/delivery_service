from typing import Any

from aiogram_dialog import DialogManager
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.query.ports.product_gateway import (
    ProductGateway,
    ProductGatewayFilters,
)
from delivery_service.application.query.product import GetAllProductsRequest
from delivery_service.domain.products.product import ProductID, ProductType


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

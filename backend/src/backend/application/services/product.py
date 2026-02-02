from decimal import Decimal

from backend.application.vars import CategoryId, Empty, ProductId, ShopId
from backend.infrastructure.persistence.tables import Product


def create_product(
    *,
    product_id: ProductId,
    shop_id: ShopId,
    name: str,
    price: Decimal,
    category_id: CategoryId | None,
) -> Product:
    return Product(
        id=product_id,
        shop_id=shop_id,
        name=name,
        price=price,
        category_id=category_id,
    )


def update_product(
    product: Product,
    *,
    name: str | None = None,
    price: Decimal | None = None,
    category_id: CategoryId | Empty | None = Empty.EMPTY,
) -> None:
    if name is not None:
        product.name = name
    if price is not None:
        product.price = price
    if category_id is not Empty.EMPTY:
        product.category_id = category_id

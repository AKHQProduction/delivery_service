from backend.application.vars import PaymentMethodId, ShopId
from backend.infrastructure.persistence.tables.shops import (
    ShopPaymentMethod,
)


def create_payment_method(
    *,
    payment_method_id: PaymentMethodId,
    shop_id: ShopId,
    name: str,
) -> ShopPaymentMethod:
    return ShopPaymentMethod(
        id=payment_method_id,
        shop_id=shop_id,
        name=name,
    )


def update_payment_method(
    payment_method: ShopPaymentMethod,
    *,
    name: str | None = None,
) -> None:
    if name is not None:
        payment_method.name = name

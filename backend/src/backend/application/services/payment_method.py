from backend.application.vars import PaymentMethodId, ShopId
from backend.infrastructure.persistence.tables.shops import (
    ShopPaymentMethod,
)

BALANCE_PAYMENT_METHOD_NAME = "Баланс"


class PaymentMethodIdentifierRequiredError(ValueError):
    def __init__(self) -> None:
        super().__init__("Either name or payment_method must be provided")


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


def is_balance_payment_method(
    *,
    name: str | None = None,
    payment_method: ShopPaymentMethod | None = None,
) -> bool:
    if payment_method is not None:
        return payment_method.name == BALANCE_PAYMENT_METHOD_NAME
    if name is not None:
        return name == BALANCE_PAYMENT_METHOD_NAME
    raise PaymentMethodIdentifierRequiredError

from dataclasses import dataclass

from backend.application.vars import PaymentMethodId


@dataclass(frozen=True)
class PaymentMethodReadModel:
    payment_method_id: PaymentMethodId
    name: str

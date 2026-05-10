from dataclasses import dataclass
from datetime import date, timedelta

from backend.application.errors import DateMustBeGreaterThanError
from backend.application.policies.access import ensure_can_manage
from backend.application.services.order_intake import (
    OrderIntake,
    OrderIntakeItem,
    OrderIntakeRequest,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    OrderId,
    PhoneId,
    ProductId,
    TimeSlotId,
    today,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.transaction_manager import TransactionManager


@dataclass(frozen=True)
class OrderProductInput:
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class CreateOrderCommand:
    client_id: ClientId
    delivery_date: date
    time_slot_id: TimeSlotId
    address_id: AddressId
    phone_id: PhoneId
    products: list[OrderProductInput]
    payment_method: str
    comment: str | None = None

    def __post_init__(self) -> None:
        current_date = today()
        if current_date > self.delivery_date:
            previous_date = current_date - timedelta(days=1)

            raise DateMustBeGreaterThanError(greater_than=previous_date)


class CreateOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        order_intake: OrderIntake,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._order_intake = order_intake
        self._tr_manager = tr_manager

    async def handle(self, command: CreateOrderCommand) -> OrderId:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        order = await self._order_intake.create(
            current_user.shop_id,
            OrderIntakeRequest(
                client_id=command.client_id,
                delivery_date=command.delivery_date,
                time_slot_id=command.time_slot_id,
                address_id=command.address_id,
                phone_id=command.phone_id,
                products=[
                    OrderIntakeItem(
                        product_id=product.product_id,
                        quantity=product.quantity,
                    )
                    for product in command.products
                ],
                payment_method=command.payment_method,
                comment=command.comment,
            ),
        )

        await self._tr_manager.commit()

        return order.id

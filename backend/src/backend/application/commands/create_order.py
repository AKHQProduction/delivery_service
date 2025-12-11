import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from backend.application.errors import (
    AccessDeniedError,
    DateMustBeGreaterThanError,
    EntityNotFoundError,
)
from backend.application.interfaces import (
    ClientGateway,
    IdentityProvider,
    TransactionManager,
)
from backend.application.interfaces.gateways.order_gateway import (
    CreateOrderDTO,
    DeliveryAddressDTO,
    OrderGateway,
    OrderItemDTO,
)
from backend.application.interfaces.gateways.product_gateway import (
    Product,
    ProductGateway,
)
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    OrderId,
    PhoneId,
    ProductId,
    TimePreference,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ProductDTO:
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class CreateOrderCommand:
    client_id: ClientId
    delivery_date: date
    time_preference: TimePreference
    address_id: AddressId
    phone_id: PhoneId
    products: list[ProductDTO]
    comment: str | None = None

    def __post_init__(self) -> None:
        today = datetime.now(UTC).date()
        if today > self.delivery_date:
            previous_date = today - timedelta(days=1)

            raise DateMustBeGreaterThanError(greater_than=previous_date)


class CreateOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: ClientGateway,
        product_gateway: ProductGateway,
        order_gateway: OrderGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._order_gateway = order_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateOrderCommand) -> OrderId:
        current_user = await self._idp.current_user()

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s trying to create order",
                current_user.user_id,
            )
            raise AccessDeniedError

        logger.info(
            "Creating new order for shop %s with client %s",
            current_user.shop_id,
            command.client_id,
        )

        client = await self._client_gateway.load(command.client_id)
        if not client:
            logger.warning("Client not found: client_id=%s", command.client_id)
            raise EntityNotFoundError(entity="Client")
        if not IsRelatedToShop(client.shop_id).is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user %s (shop_id=%s) attempted to "
                "create order for client %s",
                current_user,
                current_user.shop_id,
                command.client_id,
            )
            raise AccessDeniedError

        phone = next(
            (phone for phone in client.phones if phone.id == command.phone_id),
            None,
        )
        if not phone:
            logger.warning("Phone not found: phone_id=%s", command.phone_id)
            raise EntityNotFoundError(entity="Phone")
        address = next(
            (
                address
                for address in client.addresses
                if address.id == command.address_id
            ),
            None,
        )
        if not address:
            logger.warning(
                "Address not found: address_id=%s", command.address_id
            )
            raise EntityNotFoundError(entity="Address")

        products: list[tuple[Product, int]] = []
        for product in command.products:
            product_dm = await self._product_gateway.load(product.product_id)
            if not product_dm:
                logger.warning(
                    "Product not found: product_id=%s", product.product_id
                )
                raise EntityNotFoundError(
                    entity="Product", entity_id=product.product_id
                )
            products.append((product_dm, product.quantity))

        order_id = self._order_gateway.next_id()
        new_order = CreateOrderDTO(
            order_id=order_id,
            shop_id=current_user.shop_id,
            client_id=client.client_id,
            delivery_date=command.delivery_date,
            time_preference=command.time_preference,
            delivery_phone=phone.number,
            delivery_address=DeliveryAddressDTO(
                street=address.street,
                house=address.house,
                address_type=address.address_type,
                apartment=address.apartment,
                entrance=address.entrance,
                floor=address.floor,
                intercom=address.intercom,
            ),
            order_items=[
                OrderItemDTO(
                    name=product[0].name,
                    quantity=product[1],
                    price_per_item=product[0].price,
                )
                for product in products
            ],
            comment=command.comment,
        )

        await self._order_gateway.create_order(new_order)
        await self._tr_manager.commit()

        return order_id

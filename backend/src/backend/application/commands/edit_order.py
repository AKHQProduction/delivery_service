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
from backend.application.interfaces.gateways.client_gateway import ClientDM
from backend.application.interfaces.gateways.order_gateway import (
    DeliveryAddressDTO,
    Order,
    OrderGateway,
    UpdateOrderDTO,
    UpdateOrderItemDTO,
)
from backend.application.interfaces.gateways.product_gateway import (
    ProductGateway,
)
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    PhoneId,
    ProductId,
    TimePreference,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class NewItemDTO:
    product_id: ProductId
    quantity: int


@dataclass(frozen=True)
class ItemToUpdateDTO:
    item_id: OrderItemId
    quantity: int | None = None
    price_per_item: int | None = None
    name: str | None = None


@dataclass(frozen=True)
class UpdateOrderCommand:
    order_id: OrderId
    client_id: ClientId | None = None
    delivery_date: date | None = None
    time_preference: TimePreference | None = None
    address_id: AddressId | None = None
    phone_id: PhoneId | None = None
    comment: str | Empty | None = None
    items_to_add: list[NewItemDTO] | None = None
    items_to_update: list[ItemToUpdateDTO] | None = None
    items_to_delete: list[OrderItemId] | None = None

    def __post_init__(self) -> None:
        if self.delivery_date is not None:
            today = datetime.now(UTC).date()
            if today > self.delivery_date:
                previous_date = today - timedelta(days=1)
                raise DateMustBeGreaterThanError(greater_than=previous_date)


class UpdateOrderCommandHandler:
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

    async def handle(self, command: UpdateOrderCommand) -> None:
        current_user = await self._idp.current_user()

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s trying to update order %s",
                current_user.user_id,
                command.order_id,
            )
            raise AccessDeniedError

        order = await self._order_gateway.load(command.order_id)
        if not order:
            logger.warning("Order not found: order_id=%s", command.order_id)
            raise EntityNotFoundError(entity="Order")

        if not IsRelatedToShop(order.shop_id).is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user %s attempted to update order %s",
                current_user.user_id,
                command.order_id,
            )
            raise AccessDeniedError

        logger.info(
            "Updating order %s for shop %s",
            command.order_id,
            current_user.shop_id,
        )

        update_dto = await self._build_update_dto(command, order)

        await self._order_gateway.update(update_dto)
        await self._tr_manager.commit()

        logger.info(
            "Successfully updated order: id=%s, shop_id=%s",
            command.order_id,
            order.shop_id,
        )

    async def _build_update_dto(
        self, command: UpdateOrderCommand, order: Order
    ) -> UpdateOrderDTO:
        client_id: ClientId | None = None
        delivery_phone: str | None = None
        delivery_address: DeliveryAddressDTO | None = None
        items_to_add: list[UpdateOrderItemDTO] | None = None
        items_to_update: list[UpdateOrderItemDTO] | None = None

        # Handle client/phone/address changes
        (
            client_id,
            delivery_phone,
            delivery_address,
        ) = await self._process_client_changes(command, order)

        # Handle items to add
        if command.items_to_add:
            items_to_add = await self._process_items_to_add(
                command.items_to_add
            )

        # Handle items to update
        if command.items_to_update:
            items_to_update = [
                UpdateOrderItemDTO(
                    id=item_dto.item_id,
                    name=item_dto.name or "",
                    quantity=item_dto.quantity or 0,
                    price_per_item=item_dto.price_per_item or 0,
                )
                for item_dto in command.items_to_update
            ]

        return UpdateOrderDTO(
            order_id=command.order_id,
            client_id=client_id,
            delivery_date=command.delivery_date,
            time_preference=command.time_preference,
            delivery_phone=delivery_phone,
            delivery_address=delivery_address,
            comment=command.comment,
            items_to_add=items_to_add,
            items_to_update=items_to_update,
            items_to_delete=command.items_to_delete,
        )

    async def _process_client_changes(
        self, command: UpdateOrderCommand, order: Order
    ) -> tuple[ClientId | None, str | None, DeliveryAddressDTO | None]:
        client_id: ClientId | None = None
        delivery_phone: str | None = None
        delivery_address: DeliveryAddressDTO | None = None

        need_client_load = (
            command.client_id is not None
            or command.phone_id is not None
            or command.address_id is not None
        )

        if not need_client_load:
            return client_id, delivery_phone, delivery_address

        client_id_to_use = command.client_id or order.client_id
        client = await self._client_gateway.load(client_id_to_use)
        if not client:
            logger.warning("Client not found: client_id=%s", client_id_to_use)
            raise EntityNotFoundError(entity="Client")

        if command.client_id is not None:
            current_user = await self._idp.current_user()
            is_related = IsRelatedToShop(client.shop_id).is_satisfied_by(
                current_user
            )
            if not is_related:
                logger.warning(
                    "Access denied: client %s belongs to different shop",
                    command.client_id,
                )
                raise AccessDeniedError
            client_id = command.client_id

        if command.phone_id is not None:
            delivery_phone = self._get_phone_number(client, command.phone_id)

        if command.address_id is not None:
            delivery_address = self._get_delivery_address(
                client, command.address_id
            )

        return client_id, delivery_phone, delivery_address

    def _get_phone_number(self, client: ClientDM, phone_id: PhoneId) -> str:
        phone = next(
            (p for p in client.phones if p.id == phone_id),
            None,
        )
        if not phone:
            logger.warning("Phone not found: phone_id=%s", phone_id)
            raise EntityNotFoundError(entity="Phone")
        return phone.number

    def _get_delivery_address(
        self, client: ClientDM, address_id: AddressId
    ) -> DeliveryAddressDTO:
        address = next(
            (a for a in client.addresses if a.id == address_id),
            None,
        )
        if not address:
            logger.warning("Address not found: address_id=%s", address_id)
            raise EntityNotFoundError(entity="Address")
        return DeliveryAddressDTO(
            street=address.street,
            house=address.house,
            address_type=address.address_type,
            apartment=address.apartment,
            entrance=address.entrance,
            floor=address.floor,
            intercom=address.intercom,
        )

    async def _process_items_to_add(
        self, items: list[NewItemDTO]
    ) -> list[UpdateOrderItemDTO]:
        result: list[UpdateOrderItemDTO] = []
        for product_dto in items:
            product = await self._product_gateway.load(product_dto.product_id)
            if not product:
                logger.warning(
                    "Product not found: product_id=%s",
                    product_dto.product_id,
                )
                raise EntityNotFoundError(
                    entity="Product", entity_id=product_dto.product_id
                )
            result.append(
                UpdateOrderItemDTO(
                    name=product.name,
                    quantity=product_dto.quantity,
                    price_per_item=product.price,
                )
            )
        return result

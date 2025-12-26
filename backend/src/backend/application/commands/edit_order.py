import logging
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from backend.application.errors import (
    AccessDeniedError,
    DateMustBeGreaterThanError,
    EntityNotFoundError,
    ProductIdRequiredForNewItemError,
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
    OrderItemDTO,
    UpdateOrderDTO,
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
class OrderItem:
    quantity: int
    product_id: ProductId | None = None
    id: OrderItemId | None = None

    def __post_init__(self) -> None:
        if self.id is None and self.product_id is None:
            raise ProductIdRequiredForNewItemError


@dataclass(frozen=True)
class UpdateOrderCommand:
    order_id: OrderId
    client_id: ClientId | None = None
    delivery_date: date | None = None
    time_preference: TimePreference | None = None
    address_id: AddressId | None = None
    phone_id: PhoneId | None = None
    comment: str | Empty | None = None
    items: list[OrderItem] | None = None

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
        # Handle client/phone/address changes
        (
            client_id,
            delivery_phone,
            delivery_address,
        ) = await self._process_client_changes(command, order)

        # Handle items replacement
        items: list[OrderItemDTO] | None = None
        if command.items is not None:
            items = await self._process_items(
                command.order_id,
                command.items,  # type: ignore[arg-type]
            )
        return UpdateOrderDTO(
            order_id=command.order_id,
            client_id=client_id,
            delivery_date=command.delivery_date,
            time_preference=command.time_preference,
            delivery_phone=delivery_phone,
            delivery_address=delivery_address,
            comment=command.comment,
            items=items,
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

    @staticmethod
    def _get_phone_number(client: ClientDM, phone_id: PhoneId) -> str:
        phone = next(
            (p for p in client.phones if p.id == phone_id),
            None,
        )
        if not phone:
            logger.warning("Phone not found: phone_id=%s", phone_id)
            raise EntityNotFoundError(entity="Phone")
        return phone.number

    @staticmethod
    def _get_delivery_address(
        client: ClientDM, address_id: AddressId
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

    async def _process_items(
        self, order_id: OrderId, items: list[OrderItem]
    ) -> list[OrderItemDTO]:
        # Load existing items to get their product_id from DB
        existing_items = await self._order_gateway.load_items(order_id)
        existing_items_map = {item.id: item for item in existing_items}

        # Collect all product IDs that need to be loaded
        product_ids_to_load: set[ProductId] = set()
        item_product_map: dict[int, ProductId] = {}

        for idx, item in enumerate(items):
            product_id_to_use: ProductId | None = None

            if item.product_id is not None:
                product_id_to_use = item.product_id
            elif item.id is not None:
                existing_item = existing_items_map.get(item.id)
                if existing_item and existing_item.product_id:
                    product_id_to_use = existing_item.product_id

            if product_id_to_use is not None:
                product_ids_to_load.add(product_id_to_use)
                item_product_map[idx] = product_id_to_use

        # Batch load all products at once
        products_map: dict[ProductId, tuple[str, int]] = {}
        if product_ids_to_load:
            products = await self._product_gateway.load_many(
                list(product_ids_to_load)
            )
            products_map = {p.product_id: (p.name, p.price) for p in products}

            # Validate all products exist
            for product_id in product_ids_to_load:
                if product_id not in products_map:
                    logger.warning(
                        "Product not found: product_id=%s",
                        product_id,
                    )
                    raise EntityNotFoundError(
                        entity="Product", entity_id=product_id
                    )

        # Build result using preloaded products
        result: list[OrderItemDTO] = []
        for idx, item in enumerate(items):
            product_id_to_use = item_product_map.get(idx)
            name: str | None = None
            price_per_item: int | None = None

            if product_id_to_use is not None:
                name, price_per_item = products_map[product_id_to_use]

            result.append(
                OrderItemDTO(
                    quantity=item.quantity,
                    name=name,
                    price_per_item=price_per_item,
                    id=item.id,
                    product_id=product_id_to_use,
                )
            )

        return result

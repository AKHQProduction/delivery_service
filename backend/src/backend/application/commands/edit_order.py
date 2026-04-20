import logging
from dataclasses import dataclass
from datetime import date, time, timedelta
from decimal import Decimal

from backend.application.common import ensure_exists
from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import (
    AccessDeniedError,
    DateMustBeGreaterThanError,
    ProductIdRequiredForNewItemError,
)
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.geocoder import Geocoder
from backend.application.services.order import (
    resolve_address,
    resolve_order_items,
    resolve_phone,
    update_order,
    update_order_items,
)
from backend.application.services.order_payment import (
    apply_balance_payment,
    calculate_order_total,
    revert_balance_payment,
    sync_balance_payment_amount,
)
from backend.application.services.payment_method import (
    is_balance_payment_method,
)
from backend.application.services.route_builder import (
    insert_order_into_route,
    remove_order_from_route,
)
from backend.application.vars import (
    AddressId,
    ClientId,
    Empty,
    OrderId,
    OrderItemId,
    PhoneId,
    ProductId,
    ShopId,
    TimeSlotId,
    today,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyOrderGateway,
    SQLAlchemyProductGateway,
    SQLAlchemyRoutePlanGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.tables.base import DeliveryAddressDTO
from backend.infrastructure.persistence.tables.clients import Client
from backend.infrastructure.persistence.tables.orders import Order
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditOrderItem:
    quantity: int
    product_id: ProductId | None = None
    id: OrderItemId | None = None

    def __post_init__(self) -> None:
        if self.id is None and self.product_id is None:
            raise ProductIdRequiredForNewItemError


@dataclass(frozen=True)
class OrderPaymentSnapshot:
    client_id: ClientId
    is_balance: bool
    total: Decimal | None


@dataclass(frozen=True)
class ResolvedOrderUpdate:
    client_id: ClientId | None = None
    delivery_phone: str | None = None
    delivery_address: DeliveryAddressDTO | None = None
    delivery_start_time: time | None = None
    delivery_end_time: time | None = None


@dataclass(frozen=True)
class EditOrderCommand:
    order_id: OrderId
    client_id: ClientId | None = None
    delivery_date: date | None = None
    time_slot_id: TimeSlotId | None = None
    address_id: AddressId | None = None
    phone_id: PhoneId | None = None
    comment: str | Empty | None = None
    items: list[EditOrderItem] | None = None
    payment_method: str | None = None

    def __post_init__(self) -> None:
        if self.delivery_date is not None:
            current_date = today()
            if current_date > self.delivery_date:
                previous_date = current_date - timedelta(days=1)
                raise DateMustBeGreaterThanError(greater_than=previous_date)


class EditOrderCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        product_gateway: SQLAlchemyProductGateway,
        order_gateway: SQLAlchemyOrderGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        shop_gateway: SQLAlchemyShopGateway,
        route_plan_gateway: SQLAlchemyRoutePlanGateway,
        geocoder: Geocoder,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._product_gateway = product_gateway
        self._order_gateway = order_gateway
        self._time_slot_gateway = time_slot_gateway
        self._shop_gateway = shop_gateway
        self._route_plan_gateway = route_plan_gateway
        self._geocoder = geocoder
        self._tr_manager = tr_manager

    async def handle(self, command: EditOrderCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        order = ensure_exists(
            await self._order_gateway.load_with_items_for_update(
                command.order_id
            ),
            "Order",
        )
        ensure_related_to_shop(current_user, order.shop_id)

        logger.info(
            "Updating order %s for shop %s",
            command.order_id,
            current_user.shop_id,
        )

        payment_snapshot = self._build_payment_snapshot(order)
        resolved_update = await self._resolve_order_update(
            command=command,
            order=order,
            current_user=current_user,
        )

        update_order(
            order,
            client_id=resolved_update.client_id,
            delivery_date=command.delivery_date,
            delivery_start_time=resolved_update.delivery_start_time,
            delivery_end_time=resolved_update.delivery_end_time,
            delivery_phone=resolved_update.delivery_phone,
            delivery_address=resolved_update.delivery_address,
            comment=command.comment,
            payment_method=command.payment_method,
        )

        if (
            command.address_id is not None
            or command.delivery_date is not None
            or command.time_slot_id is not None
        ):
            await self._update_route_position(order, command.time_slot_id)

        if command.items is not None:
            await self._process_items(command, order)

        next_is_balance = is_balance_payment_method(name=order.payment_method)
        if payment_snapshot.is_balance or next_is_balance:
            await self._sync_balance_payment(
                order=order,
                previous_client_id=payment_snapshot.client_id,
                previous_is_balance=payment_snapshot.is_balance,
                next_is_balance=next_is_balance,
                previous_total=payment_snapshot.total,
            )

        await self._tr_manager.commit()

        logger.info(
            "Successfully updated order: id=%s, shop_id=%s",
            command.order_id,
            order.shop_id,
        )

    def _build_payment_snapshot(self, order: Order) -> OrderPaymentSnapshot:
        is_balance = is_balance_payment_method(name=order.payment_method)
        return OrderPaymentSnapshot(
            client_id=order.client_id,
            is_balance=is_balance,
            total=calculate_order_total(order) if is_balance else None,
        )

    async def _resolve_order_update(
        self,
        *,
        command: EditOrderCommand,
        order: Order,
        current_user: CurrentUserDTO,
    ) -> ResolvedOrderUpdate:
        client_update = await self._resolve_client_update(
            command=command,
            order=order,
            current_user=current_user,
        )
        time_slot_update = await self._resolve_time_slot_update(
            command.time_slot_id,
            current_user,
        )
        return ResolvedOrderUpdate(
            client_id=client_update.client_id,
            delivery_phone=client_update.delivery_phone,
            delivery_address=client_update.delivery_address,
            delivery_start_time=time_slot_update.delivery_start_time,
            delivery_end_time=time_slot_update.delivery_end_time,
        )

    async def _resolve_client_update(
        self,
        *,
        command: EditOrderCommand,
        order: Order,
        current_user: CurrentUserDTO,
    ) -> ResolvedOrderUpdate:
        if (
            command.client_id is None
            and command.phone_id is None
            and command.address_id is None
        ):
            return ResolvedOrderUpdate()

        client_id = command.client_id or order.client_id
        client = ensure_exists(
            await self._client_gateway.load(client_id),
            "Client",
        )

        next_client_id = (
            command.client_id if command.client_id is not None else None
        )
        if next_client_id is not None:
            ensure_related_to_shop(current_user, client.shop_id)

        delivery_phone = (
            resolve_phone(client, command.phone_id)
            if command.phone_id is not None
            else None
        )
        delivery_address = await self._resolve_delivery_address(
            client=client,
            address_id=command.address_id,
            shop_id=current_user.shop_id,
        )

        return ResolvedOrderUpdate(
            client_id=next_client_id,
            delivery_phone=delivery_phone,
            delivery_address=delivery_address,
        )

    async def _resolve_delivery_address(
        self,
        *,
        client: Client,
        address_id: AddressId | None,
        shop_id: ShopId,
    ) -> DeliveryAddressDTO | None:
        if address_id is None:
            return None

        delivery_address = resolve_address(client, address_id)
        if delivery_address.coordinates is not None:
            return delivery_address

        shop = await self._shop_gateway.load_shop(shop_id)
        shop_city = shop.city if shop else None
        coords = await self._geocoder.geocode_if_missing(
            street=delivery_address.street,
            house=delivery_address.house,
            coordinates=None,
            shop_city=shop_city,
            require_house=False,
        )
        if coords is not None:
            delivery_address.coordinates = coords
            addr_obj = next(a for a in client.addresses if a.id == address_id)
            coords.apply_to(addr_obj)

        return delivery_address

    async def _resolve_time_slot_update(
        self,
        time_slot_id: TimeSlotId | None,
        current_user: CurrentUserDTO,
    ) -> ResolvedOrderUpdate:
        if time_slot_id is None:
            return ResolvedOrderUpdate()

        time_slot = ensure_exists(
            await self._time_slot_gateway.load(time_slot_id),
            "TimeSlot",
        )
        ensure_related_to_shop(current_user, time_slot.shop_id)
        return ResolvedOrderUpdate(
            delivery_start_time=time_slot.start_time,
            delivery_end_time=time_slot.end_time,
        )

    async def _update_route_position(
        self, order: Order, new_time_slot_id: TimeSlotId | None
    ) -> None:
        old_route_plan = await self._route_plan_gateway.find_by_order(order.id)
        if old_route_plan:
            remove_order_from_route(old_route_plan, order.id)
            logger.info(
                "Removed order %s from route plan %s",
                order.id,
                old_route_plan.id,
            )

        target_slot_id = (
            new_time_slot_id
            if new_time_slot_id is not None
            else (old_route_plan.time_slot_id if old_route_plan else None)
        )

        target_plan = await self._route_plan_gateway.load_by_date(
            shop_id=order.shop_id,
            delivery_date=order.date,
            time_slot_id=target_slot_id,
        )
        if not target_plan:
            logger.info(
                "No target route plan for order %s (date=%s, slot=%s)",
                order.id,
                order.date,
                target_slot_id,
            )
            return

        shop = await self._shop_gateway.load_shop(order.shop_id)
        shop_coords = CoordinatesDTO.build(
            shop.latitude if shop else None,
            shop.longitude if shop else None,
        )
        all_orders = await self._order_gateway.load_by_date(
            shop_id=order.shop_id,
            delivery_date=order.date,
            start_time=order.delivery_start_time,
            end_time=order.delivery_end_time,
        )
        insert_order_into_route(target_plan, order, shop_coords, all_orders)
        logger.info(
            "Inserted order %s into route plan %s",
            order.id,
            target_plan.id,
        )

    async def _process_items(
        self,
        command: EditOrderCommand,
        order: Order,
    ) -> None:
        product_ids = {
            item.product_id
            for item in command.items  # type: ignore[union-attr]
            if item.product_id is not None
        }
        existing_product_ids = {
            item.product_id
            for item in order.items
            if item.product_id is not None
        }
        all_product_ids = list(product_ids | existing_product_ids)

        products = (
            await self._product_gateway.load_many(all_product_ids)
            if all_product_ids
            else []
        )
        for pid in product_ids:
            ensure_exists(
                next((p for p in products if p.id == pid), None),
                "Product",
            )

        item_dtos = resolve_order_items(
            items=[
                (item.id, item.quantity, item.product_id)
                for item in command.items  # type: ignore[union-attr]
            ],
            existing_items=order.items,
            products=products,
        )
        removed = update_order_items(order, item_dtos)
        await self._order_gateway.delete_items(removed)

    async def _sync_balance_payment(
        self,
        *,
        order: Order,
        previous_client_id: ClientId,
        previous_is_balance: bool,
        next_is_balance: bool,
        previous_total: Decimal | None,
    ) -> None:
        previous_client = None
        if previous_is_balance:
            previous_client = ensure_exists(
                await self._client_gateway.load_for_update(previous_client_id),
                "Client",
            )
            if previous_client.shop_id != order.shop_id:
                raise AccessDeniedError

        current_client = None
        if next_is_balance:
            if (
                previous_client is not None
                and previous_client.id == order.client_id
            ):
                current_client = previous_client
            else:
                current_client = ensure_exists(
                    await self._client_gateway.load_for_update(
                        order.client_id
                    ),
                    "Client",
                )
                if current_client.shop_id != order.shop_id:
                    raise AccessDeniedError

        if previous_is_balance and next_is_balance:
            assert previous_client is not None
            assert current_client is not None
            if previous_client_id != order.client_id:
                revert_balance_payment(
                    order,
                    previous_client,
                    total=previous_total,
                )
                apply_balance_payment(order, current_client)
            else:
                sync_balance_payment_amount(
                    order=order,
                    client=current_client,
                    previous_total=previous_total or Decimal(0),
                )
            return

        if previous_is_balance:
            assert previous_client is not None
            revert_balance_payment(
                order,
                previous_client,
                total=previous_total,
            )
            return

        if next_is_balance:
            assert current_client is not None
            apply_balance_payment(order, current_client)

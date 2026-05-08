import datetime
import logging
from dataclasses import dataclass
from decimal import Decimal

from backend.application.common import ensure_exists
from backend.application.dto.coordinates import CoordinatesDTO
from backend.application.dto.idp import CurrentUserDTO
from backend.application.errors import InvalidPrimaryFlagError
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.services.client import (
    AddressSyncItem,
    PhoneSyncItem,
    check_phone_duplicates,
    sync_addresses,
    sync_phones,
    update_client,
)
from backend.application.services.geocoder import Geocoder
from backend.application.validators import normalize_ukraine_phone
from backend.application.validators.phone import validate_no_duplicate_phones
from backend.application.vars import (
    AddressId,
    ClientId,
    DistrictId,
    PhoneId,
    RecurringOrderStatus,
    TimeSlotId,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
    SQLAlchemyRecurringOrderGateway,
    SQLAlchemyShopGateway,
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.persistence.gateways.order_gateway import (
    SQLAlchemyOrderGateway,
)
from backend.infrastructure.persistence.tables.clients import ClientAddress
from backend.infrastructure.persistence.tables.recurring_orders import (
    RecurringOrder,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Phone:
    number: str
    is_primary: bool = False
    id: PhoneId | None = None


@dataclass(frozen=True)
class Address:
    street: str
    house: str
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    comment: str | None = None
    coordinates: CoordinatesDTO | None = None
    is_primary: bool = False
    id: AddressId | None = None
    district_id: DistrictId | None = None
    preferred_time_slot_id: TimeSlotId | None = None


@dataclass(frozen=True)
class EditClientCommand:
    client_id: ClientId
    full_name: str | None = None
    balance: Decimal | None = None
    phones: list[Phone] | None = None
    addresses: list[Address] | None = None
    confirm_duplicate_phones: bool = False

    def __post_init__(self) -> None:
        if self.phones is not None and self.phones:
            primary_count = sum(1 for phone in self.phones if phone.is_primary)
            if primary_count != 1:
                raise InvalidPrimaryFlagError(
                    field="phone", count=primary_count
                )

        if self.addresses is not None and self.addresses:
            primary_count = sum(
                1 for address in self.addresses if address.is_primary
            )
            if primary_count != 1:
                raise InvalidPrimaryFlagError(
                    field="address", count=primary_count
                )


class EditClientCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        shop_gateway: SQLAlchemyShopGateway,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        order_gateway: SQLAlchemyOrderGateway,
        recurring_order_gateway: SQLAlchemyRecurringOrderGateway,
        geocoder: Geocoder,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._shop_gateway = shop_gateway
        self._time_slot_gateway = time_slot_gateway
        self._order_gateway = order_gateway
        self._recurring_order_gateway = recurring_order_gateway
        self._geocoder = geocoder
        self._tr_manager = tr_manager

    async def handle(self, command: EditClientCommand) -> None:  # noqa: PLR0914
        logger.info(
            "Editing client: client_id=%s, new_full_name=%s, "
            "phones=%s, addresses=%s",
            command.client_id,
            command.full_name,
            len(command.phones) if command.phones else None,
            len(command.addresses) if command.addresses else None,
        )

        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        client = ensure_exists(
            await self._client_gateway.load(client_id=command.client_id),
            "Client",
        )
        ensure_related_to_shop(current_user, client.shop_id)

        updates = []
        old_phone_numbers = {phone.id: phone.number for phone in client.phones}
        old_address_keys = {
            address.id: self._address_key_from_model(address)
            for address in client.addresses
        }
        recurring_orders_to_repoint = (
            await self._recurring_order_gateway.load_by_client_refs(
                client.id,
                phone_ids=set(old_phone_numbers)
                if command.phones is not None
                else set(),
                address_ids=set(old_address_keys)
                if command.addresses is not None
                else set(),
            )
        )

        if command.full_name is not None or command.balance is not None:
            update_client(
                client,
                full_name=command.full_name,
                balance=command.balance,
            )
            if command.full_name is not None:
                updates.append(f"full_name={command.full_name}")
            if command.balance is not None:
                updates.append(f"balance={command.balance}")

        if command.phones is not None:
            normalized_phones = [
                PhoneSyncItem(
                    number=normalize_ukraine_phone(p.number),
                    is_primary=p.is_primary,
                    id=p.id,
                )
                for p in command.phones
            ]

            normalized_numbers = [p.number for p in normalized_phones]
            validate_no_duplicate_phones(
                normalized_numbers,
                client_id=client.id,
                full_name=client.full_name,
            )

            if not command.confirm_duplicate_phones and normalized_numbers:
                await check_phone_duplicates(
                    client_gateway=self._client_gateway,
                    shop_id=client.shop_id,
                    phone_numbers=normalized_numbers,
                    exclude_client_id=command.client_id,
                )

            sync_phones(
                client, phones=normalized_phones, shop_id=client.shop_id
            )
            updates.append(f"phones={len(command.phones)}")

        if command.addresses is not None:
            await self._ensure_address_time_slots_related_to_shop(
                current_user, command.addresses
            )
            shop = await self._shop_gateway.load_shop(client.shop_id)
            shop_city = shop.city if shop else None

            old_coords = {
                addr.id: (addr.latitude, addr.longitude)
                for addr in client.addresses
            }

            address_items = []
            for a in command.addresses:
                coordinates = await self._geocoder.geocode_if_missing(
                    street=a.street,
                    house=a.house,
                    coordinates=a.coordinates,
                    shop_city=shop_city,
                )
                address_items.append(
                    AddressSyncItem(
                        street=a.street,
                        house=a.house,
                        apartment=a.apartment,
                        entrance=a.entrance,
                        floor=a.floor,
                        intercom=a.intercom,
                        comment=a.comment,
                        coordinates=coordinates,
                        is_primary=a.is_primary,
                        district_id=a.district_id,
                        id=a.id,
                        preferred_time_slot_id=a.preferred_time_slot_id,
                    )
                )

            sync_addresses(client, addresses=address_items)

            today = datetime.datetime.now(datetime.UTC).date()
            for item in address_items:
                if not item.id or not item.coordinates:
                    continue
                old = old_coords.get(item.id)
                if not old:
                    continue
                old_lat, old_lng = old
                if (item.coordinates.latitude, item.coordinates.longitude) == (
                    old_lat,
                    old_lng,
                ):
                    continue
                updated = (
                    await self._order_gateway.update_delivery_coordinates(
                        shop_id=client.shop_id,
                        client_id=client.id,
                        street=item.street,
                        house=item.house,
                        new_coordinates=item.coordinates,
                        from_date=today,
                    )
                )
                if updated:
                    logger.info(
                        "Propagated coordinates to %d order(s) for "
                        "client_id=%s, street=%s, house=%s",
                        updated,
                        client.id,
                        item.street,
                        item.house,
                    )

            updates.append(f"addresses={len(command.addresses)}")

        if command.phones is not None or command.addresses is not None:
            await self._tr_manager.flush()
            self._repoint_recurring_order_refs(
                recurring_orders_to_repoint,
                old_phone_numbers=old_phone_numbers
                if command.phones is not None
                else {},
                old_address_keys=old_address_keys
                if command.addresses is not None
                else {},
                current_phone_ids={phone.id for phone in client.phones},
                current_address_ids={
                    address.id for address in client.addresses
                },
                new_phone_by_number={
                    phone.number: phone.id for phone in client.phones
                },
                new_address_by_key={
                    self._address_key_from_model(address): address.id
                    for address in client.addresses
                },
            )

        await self._tr_manager.commit()

        logger.info(
            "Successfully edited client: id=%s, shop_id=%s, updates={%s}",
            command.client_id,
            client.shop_id,
            ", ".join(updates),
        )

    async def _ensure_address_time_slots_related_to_shop(
        self,
        current_user: CurrentUserDTO,
        addresses: list[Address],
    ) -> None:
        for address in addresses:
            if address.preferred_time_slot_id is None:
                continue
            time_slot = ensure_exists(
                await self._time_slot_gateway.load(
                    address.preferred_time_slot_id
                ),
                "TimeSlot",
            )
            ensure_related_to_shop(current_user, time_slot.shop_id)

    def _repoint_recurring_order_refs(
        self,
        recurring_orders: list[RecurringOrder],
        *,
        old_phone_numbers: dict[PhoneId, str],
        old_address_keys: dict[AddressId, tuple[str, ...]],
        current_phone_ids: set[PhoneId],
        current_address_ids: set[AddressId],
        new_phone_by_number: dict[str, PhoneId],
        new_address_by_key: dict[tuple[str, ...], AddressId],
    ) -> None:
        for recurring_order in recurring_orders:
            if (
                recurring_order.phone_id in old_phone_numbers
                and recurring_order.phone_id not in current_phone_ids
            ):
                new_phone_id = new_phone_by_number.get(
                    old_phone_numbers[recurring_order.phone_id]
                )
                recurring_order.phone_id = new_phone_id
                if new_phone_id is None:
                    recurring_order.status = RecurringOrderStatus.PAUSED

            if (
                recurring_order.address_id in old_address_keys
                and recurring_order.address_id not in current_address_ids
            ):
                new_address_id = new_address_by_key.get(
                    old_address_keys[recurring_order.address_id]
                )
                recurring_order.address_id = new_address_id
                if new_address_id is None:
                    recurring_order.status = RecurringOrderStatus.PAUSED

    def _address_key_from_model(
        self, address: ClientAddress
    ) -> tuple[str, ...]:
        return (
            address.street,
            address.house,
            address.apartment or "",
            address.entrance or "",
            address.floor or "",
            address.intercom or "",
            address.comment or "",
        )

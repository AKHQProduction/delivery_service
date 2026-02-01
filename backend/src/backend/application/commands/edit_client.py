import logging
from dataclasses import dataclass

from backend.application.errors import (
    ExistingClientInfo,
    InvalidPrimaryFlagError,
    PhoneDuplicate,
    PhoneNumberAlreadyExistsError,
)
from backend.application.policies.access import (
    ensure_can_manage,
    ensure_related_to_shop,
)
from backend.application.validators import normalize_ukraine_phone
from backend.application.vars import AddressId, ClientId, PhoneId
from backend.domain.services.client import (
    create_address,
    create_phone,
    update_address,
    update_client,
    update_phone,
)
from backend.domain.services.common import ensure_exists
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
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
    is_primary: bool = False
    id: AddressId | None = None


@dataclass(frozen=True)
class EditClientCommand:
    client_id: ClientId
    full_name: str | None = None
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
        idp: TelegramIdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditClientCommand) -> None:
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

        if command.full_name is not None:
            update_client(client, full_name=command.full_name)
            updates.append(f"full_name={command.full_name}")

        if command.phones is not None:
            normalized_phones = [
                Phone(
                    number=normalize_ukraine_phone(p.number),
                    is_primary=p.is_primary,
                    id=p.id,
                )
                for p in command.phones
            ]

            if not command.confirm_duplicate_phones and normalized_phones:
                normalized_numbers = [p.number for p in normalized_phones]
                duplicates = await self._client_gateway.find_duplicate_phones(
                    shop_id=client.shop_id,
                    phone_numbers=normalized_numbers,
                    exclude_client_id=command.client_id,
                )
                if duplicates:
                    raise PhoneNumberAlreadyExistsError(
                        duplicates=[
                            PhoneDuplicate(
                                phone_number=dup.phone_number,
                                existing_clients=[
                                    ExistingClientInfo(
                                        client_id=o.client_id,
                                        full_name=o.full_name,
                                    )
                                    for o in dup.owners
                                ],
                            )
                            for dup in duplicates
                        ]
                    )

            existing_phones = {p.id: p for p in client.phones}
            updated_phone_ids = {p.id for p in normalized_phones if p.id}

            for phone_data in normalized_phones:
                if phone_data.id and phone_data.id in existing_phones:
                    update_phone(
                        existing_phones[phone_data.id],
                        number=phone_data.number,
                        is_primary=phone_data.is_primary,
                    )
                else:
                    new_phone = create_phone(
                        number=phone_data.number,
                        is_primary=phone_data.is_primary,
                        shop_id=client.shop_id,
                    )
                    client.phones.append(new_phone)

            for phone_id, phone in existing_phones.items():
                if phone_id not in updated_phone_ids:
                    client.phones.remove(phone)

            updates.append(f"phones={len(command.phones)}")

        if command.addresses is not None:
            existing_addresses = {a.id: a for a in client.addresses}
            updated_addr_ids = {a.id for a in command.addresses if a.id}

            for addr_data in command.addresses:
                if addr_data.id and addr_data.id in existing_addresses:
                    update_address(
                        existing_addresses[addr_data.id],
                        street=addr_data.street,
                        house=addr_data.house,
                        apartment=addr_data.apartment,
                        entrance=addr_data.entrance,
                        floor=addr_data.floor,
                        intercom=addr_data.intercom,
                        comment=addr_data.comment,
                        is_primary=addr_data.is_primary,
                    )
                else:
                    new_address = create_address(
                        street=addr_data.street,
                        house=addr_data.house,
                        apartment=addr_data.apartment,
                        entrance=addr_data.entrance,
                        floor=addr_data.floor,
                        intercom=addr_data.intercom,
                        comment=addr_data.comment,
                        is_primary=addr_data.is_primary,
                    )
                    client.addresses.append(new_address)

            for addr_id, addr in existing_addresses.items():
                if addr_id not in updated_addr_ids:
                    client.addresses.remove(addr)

            updates.append(f"addresses={len(command.addresses)}")

        await self._tr_manager.commit()

        logger.info(
            "Successfully edited client: id=%s, shop_id=%s, updates={%s}",
            command.client_id,
            client.shop_id,
            ", ".join(updates),
        )

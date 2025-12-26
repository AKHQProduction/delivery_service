import logging
from dataclasses import dataclass

from backend.application.errors import (
    AccessDeniedError,
    EntityNotFoundError,
    InvalidPrimaryFlagError,
    PhoneNumberAlreadyExistsError,
)
from backend.application.interfaces import (
    ClientGateway,
    IdentityProvider,
    TransactionManager,
)
from backend.application.interfaces.gateways.client_gateway import (
    AddressDTO,
    PhoneDTO,
)
from backend.application.policies.access import (
    IsRelatedToShop,
    can_shop_manage_policy,
)
from backend.application.vars import AddressId, AddressType, ClientId, PhoneId

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
    address_type: AddressType
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    is_primary: bool = False
    id: AddressId | None = None


@dataclass(frozen=True)
class EditClientCommand:
    client_id: ClientId
    full_name: str | None = None
    custom_id: str | None = None
    phones: list[Phone] | None = None
    addresses: list[Address] | None = None

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
        client_gateway: ClientGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditClientCommand) -> None:
        logger.info(
            "Editing client: client_id=%s, new_full_name=%s, "
            "new_custom_id=%s, phones=%s, addresses=%s",
            command.client_id,
            command.full_name,
            command.custom_id,
            len(command.phones) if command.phones else None,
            len(command.addresses) if command.addresses else None,
        )

        current_user = await self._idp.current_user()
        logger.debug(
            "Current user retrieved", extra={"user_id": current_user.user_id}
        )

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s when editing client %s",
                current_user,
                command.client_id,
            )
            raise AccessDeniedError

        client = await self._client_gateway.load(client_id=command.client_id)
        if not client:
            logger.warning("Client not found: client_id=%s", command.client_id)
            raise EntityNotFoundError(entity="Client")

        if not IsRelatedToShop(client.shop_id).is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user %s (shop_id=%s) attempted to edit "
                "client %s (shop_id=%s)",
                current_user,
                current_user.shop_id,
                command.client_id,
                client.shop_id,
            )
            raise AccessDeniedError

        updates = []

        if command.full_name is not None:
            client.full_name = command.full_name
            updates.append(f"full_name={command.full_name}")

        if command.custom_id is not None:
            client.custom_id = command.custom_id
            updates.append(f"custom_id={command.custom_id}")

        if command.phones is not None:
            current_numbers = {phone.number for phone in client.phones}
            new_numbers = [
                phone.number
                for phone in command.phones
                if phone.number not in current_numbers
            ]

            if new_numbers:
                existing = await self._client_gateway.check_existing_numbers(
                    new_numbers
                )
                if existing:
                    duplicate = next(iter(existing))
                    logger.warning(
                        "Phone number %s already exists for another client",
                        duplicate,
                    )
                    raise PhoneNumberAlreadyExistsError(duplicate)

            client.phones = [
                PhoneDTO(
                    number=phone.number,
                    is_primary=phone.is_primary,
                    id=phone.id,
                )
                for phone in command.phones
            ]
            updates.append(f"phones={len(command.phones)}")

        if command.addresses is not None:
            client.addresses = [
                AddressDTO(
                    street=address.street,
                    house=address.house,
                    address_type=address.address_type,
                    apartment=address.apartment,
                    entrance=address.entrance,
                    floor=address.floor,
                    intercom=address.intercom,
                    is_primary=address.is_primary,
                    id=address.id,
                )
                for address in command.addresses
            ]
            updates.append(f"addresses={len(command.addresses)}")

        logger.debug(
            "Updating client %s: %s", command.client_id, ", ".join(updates)
        )

        await self._client_gateway.update(client)
        await self._tr_manager.commit()

        logger.info(
            "Successfully edited client: id=%s, shop_id=%s, updates={%s}",
            command.client_id,
            client.shop_id,
            ", ".join(updates),
        )

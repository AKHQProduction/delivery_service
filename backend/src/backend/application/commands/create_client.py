import logging
from dataclasses import dataclass, field

from backend.application.errors import (
    ExistingClientInfo,
    PhoneDuplicate,
    PhoneNumberAlreadyExistsError,
)
from backend.application.policies.access import ensure_can_manage
from backend.application.services.client import (
    create_address,
    create_client,
    create_phone,
)
from backend.application.validators import normalize_ukraine_phone
from backend.application.validators.phone import validate_no_duplicate_phones
from backend.application.vars import ClientId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyClientGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Address:
    street: str
    house: str
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None
    comment: str | None = None


@dataclass(frozen=True)
class Phone:
    number: str


@dataclass(frozen=True)
class CreateClientCommand:
    full_name: str
    phones: list[Phone] = field(default_factory=list)
    addresses: list[Address] = field(default_factory=list)
    confirm_duplicate_phones: bool = False


class CreateClientCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateClientCommand) -> ClientId:
        current_user = await self._idp.current_user()
        ensure_can_manage(current_user)

        logger.info(
            "Creating new client '%s' for shop %s",
            command.full_name,
            current_user.shop_id,
        )

        normalized_numbers = [
            normalize_ukraine_phone(phone.number) for phone in command.phones
        ]

        if normalized_numbers:
            validate_no_duplicate_phones(
                normalized_numbers, full_name=command.full_name
            )

        if not command.confirm_duplicate_phones and normalized_numbers:
            duplicates = await self._client_gateway.find_duplicate_phones(
                shop_id=current_user.shop_id,
                phone_numbers=normalized_numbers,
            )
            if duplicates:
                raise PhoneNumberAlreadyExistsError(
                    duplicates=[
                        PhoneDuplicate(
                            phone_number=dup.phone_number,
                            existing_clients=[
                                ExistingClientInfo(
                                    client_id=owner.client_id,
                                    full_name=owner.full_name,
                                )
                                for owner in dup.owners
                            ],
                        )
                        for dup in duplicates
                    ]
                )

        client_id = self._client_gateway.next_id()
        client = create_client(
            client_id=client_id,
            shop_id=current_user.shop_id,
            full_name=command.full_name,
        )

        client.phones = [
            create_phone(
                number=normalized_numbers[idx],
                is_primary=(idx == 0),
                shop_id=current_user.shop_id,
            )
            for idx in range(len(command.phones))
        ]

        client.addresses = [
            create_address(
                street=addr.street,
                house=addr.house,
                apartment=addr.apartment,
                entrance=addr.entrance,
                floor=addr.floor,
                intercom=addr.intercom,
                comment=addr.comment,
                is_primary=(idx == 0),
            )
            for idx, addr in enumerate(command.addresses)
        ]

        self._client_gateway.save(client)
        await self._tr_manager.commit()

        logger.info(
            "Client '%s' (id=%s) created successfully with %d "
            "phone(s) and %d address(es)",
            command.full_name,
            client_id,
            len(command.phones),
            len(command.addresses),
        )

        return client_id

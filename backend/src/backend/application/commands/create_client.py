import logging
from dataclasses import dataclass, field

from backend.application.errors import (
    AccessDeniedError,
    ExistingClientInfo,
    PhoneDuplicate,
    PhoneNumberAlreadyExistsError,
)
from backend.application.interfaces import IdentityProvider, TransactionManager
from backend.application.interfaces.gateways.client_gateway import (
    AddressDTO,
    ClientGateway,
    CreateClientDTO,
    PhoneDTO,
)
from backend.application.policies.access import can_shop_manage_policy
from backend.application.validators import normalize_ukraine_phone
from backend.application.vars import ClientId

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
        idp: IdentityProvider,
        client_gateway: ClientGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateClientCommand) -> ClientId:
        current_user = await self._idp.current_user()

        if not can_shop_manage_policy.is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s trying to create client",
                current_user.user_id,
            )
            raise AccessDeniedError

        logger.info(
            "Creating new client '%s' for shop %s",
            command.full_name,
            current_user.shop_id,
        )

        phones_dto = [
            PhoneDTO(
                number=normalize_ukraine_phone(phone.number),
                is_primary=(idx == 0),
            )
            for idx, phone in enumerate(command.phones)
        ]

        if not command.confirm_duplicate_phones and phones_dto:
            normalized_numbers = [p.number for p in phones_dto]
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

        addresses_dto = [
            AddressDTO(
                street=address.street,
                house=address.house,
                apartment=address.apartment,
                entrance=address.entrance,
                floor=address.floor,
                intercom=address.intercom,
                comment=address.comment,
                is_primary=(idx == 0),
            )
            for idx, address in enumerate(command.addresses)
        ]

        client_id = self._client_gateway.next_id()
        create_dto = CreateClientDTO(
            client_id=client_id,
            shop_id=current_user.shop_id,
            full_name=command.full_name,
            phones=phones_dto,
            addresses=addresses_dto,
        )

        await self._client_gateway.create_client(create_dto)
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

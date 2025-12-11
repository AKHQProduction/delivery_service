import logging
from dataclasses import dataclass, field

from backend.application.errors import (
    AccessDeniedError,
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
from backend.application.vars import AddressType, ClientId

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Address:
    street: str
    house: str
    address_type: AddressType
    apartment: str | None = None
    entrance: str | None = None
    floor: str | None = None
    intercom: str | None = None


@dataclass(frozen=True)
class Phone:
    number: str


@dataclass(frozen=True)
class CreateClientCommand:
    full_name: str
    phones: list[Phone] = field(default_factory=list)
    addresses: list[Address] = field(default_factory=list)
    custom_id: str | None = None


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

        for phone in command.phones:
            if await self._client_gateway.exists_with_number(phone.number):
                logger.warning(
                    "Phone number %s already exists for another client",
                    phone.number,
                )
                raise PhoneNumberAlreadyExistsError(phone.number)

        phones_dto = [
            PhoneDTO(number=phone.number, is_primary=(idx == 0))
            for idx, phone in enumerate(command.phones)
        ]

        addresses_dto = [
            AddressDTO(
                street=address.street,
                house=address.house,
                address_type=address.address_type,
                apartment=address.apartment,
                entrance=address.entrance,
                floor=address.floor,
                intercom=address.intercom,
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
            custom_id=command.custom_id,
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

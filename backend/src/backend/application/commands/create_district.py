import logging
from dataclasses import dataclass

from backend.application.errors import AlreadyExistsError
from backend.application.policies.access import ensure_is_owner
from backend.application.services.district import create_district
from backend.application.vars import DistrictId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyDistrictGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateDistrictCommand:
    name: str


class CreateDistrictCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        gateway: SQLAlchemyDistrictGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._gateway = gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateDistrictCommand) -> DistrictId:
        logger.info("Creating district: name=%s", command.name)

        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        if await self._gateway.exists_by_name_in_shop(
            command.name, current_user.shop_id
        ):
            raise AlreadyExistsError(entity="District")

        district_id = self._gateway.next_id()

        district = create_district(
            district_id=district_id,
            shop_id=current_user.shop_id,
            name=command.name,
        )
        self._gateway.save(district)
        await self._tr_manager.commit()

        logger.info(
            "Successfully created district: id=%s, name=%s, shop_id=%s",
            district_id,
            command.name,
            current_user.shop_id,
        )
        return district_id

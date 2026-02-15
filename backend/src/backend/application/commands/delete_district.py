import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_is_owner,
    ensure_related_to_shop,
)
from backend.application.vars import DistrictId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyDistrictGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteDistrictCommand:
    district_id: DistrictId


class DeleteDistrictCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        district_gateway: SQLAlchemyDistrictGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._district_gateway = district_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteDistrictCommand) -> None:
        logger.info(
            "Deleting district: district_id=%s",
            command.district_id,
        )

        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        district = await self._district_gateway.load(command.district_id)
        if not district:
            return

        ensure_related_to_shop(current_user, district.shop_id)

        await self._district_gateway.delete(district)
        await self._tr_manager.commit()

        logger.info(
            "Successfully deleted district: id=%s, shop_id=%s",
            command.district_id,
            district.shop_id,
        )

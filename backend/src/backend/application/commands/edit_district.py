import logging
from dataclasses import dataclass

from backend.application.common import ensure_exists
from backend.application.errors import AlreadyExistsError
from backend.application.policies.access import (
    ensure_is_owner,
    ensure_related_to_shop,
)
from backend.application.services.district import update_district
from backend.application.vars import DistrictId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyDistrictGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditDistrictCommand:
    district_id: DistrictId
    new_name: str | None = None


class EditDistrictCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        district_gateway: SQLAlchemyDistrictGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._district_gateway = district_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditDistrictCommand) -> None:
        logger.info(
            "Editing district: district_id=%s, new_name=%s",
            command.district_id,
            command.new_name,
        )

        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        district = ensure_exists(
            await self._district_gateway.load(command.district_id),
            "District",
        )
        ensure_related_to_shop(current_user, district.shop_id)

        if command.new_name:
            if await self._district_gateway.exists_by_name_in_shop(
                command.new_name, current_user.shop_id
            ):
                raise AlreadyExistsError(entity="District")
            update_district(district, name=command.new_name)

        await self._tr_manager.commit()

        logger.info(
            "Successfully edited district: id=%s, shop_id=%s",
            command.district_id,
            district.shop_id,
        )

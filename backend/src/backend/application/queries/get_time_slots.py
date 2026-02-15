import logging

from backend.application.dto.gateways.time_slot_gateway import (
    TimeSlotReadModel,
)
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyTimeSlotGateway,
)

logger = logging.getLogger(__name__)


class GetTimeSlotsQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
    ) -> None:
        self._idp = idp
        self._time_slot_gateway = time_slot_gateway

    async def handle(self) -> list[TimeSlotReadModel]:
        current_user = await self._idp.current_user()

        time_slots = await self._time_slot_gateway.load_by_shop(
            current_user.shop_id
        )

        logger.info(
            "Retrieved %d time slots for shop %s",
            len(time_slots),
            current_user.shop_id,
        )

        return time_slots

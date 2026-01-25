import logging

from backend.application.interfaces import IdentityProvider
from backend.application.interfaces.gateways.time_slot_gateway import (
    TimeSlotGateway,
    TimeSlotReadModel,
)

logger = logging.getLogger(__name__)


class GetTimeSlotsQueryHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        time_slot_gateway: TimeSlotGateway,
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

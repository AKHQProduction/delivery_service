import logging
from dataclasses import dataclass
from datetime import time

from backend.application.errors import AlreadyExistsError
from backend.application.policies.access import ensure_is_owner
from backend.application.services.time_slot import create_time_slot
from backend.application.validators.time import validate_time_slot_range
from backend.application.vars import TimeSlotId
from backend.infrastructure.idp import IdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CreateTimeSlotCommand:
    start_time: time
    end_time: time
    label: str | None = None

    def __post_init__(self) -> None:
        validate_time_slot_range(self.start_time, self.end_time)


class CreateTimeSlotCommandHandler:
    def __init__(
        self,
        idp: IdentityProvider,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._time_slot_gateway = time_slot_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: CreateTimeSlotCommand) -> TimeSlotId:
        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        if await self._time_slot_gateway.exists_by_times_in_shop(
            current_user.shop_id, command.start_time, command.end_time
        ):
            raise AlreadyExistsError(entity="TimeSlot")

        time_slot_id = self._time_slot_gateway.next_id()

        time_slot = create_time_slot(
            time_slot_id=time_slot_id,
            shop_id=current_user.shop_id,
            start_time=command.start_time,
            end_time=command.end_time,
            label=command.label,
        )
        self._time_slot_gateway.save(time_slot)

        await self._tr_manager.commit()

        logger.info(
            "Time slot %s created for shop %s",
            time_slot_id,
            current_user.shop_id,
        )

        return time_slot_id

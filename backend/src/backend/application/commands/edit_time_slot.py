import logging
from dataclasses import dataclass
from datetime import time

from backend.application.common import ensure_exists
from backend.application.errors import AlreadyExistsError
from backend.application.policies.access import (
    ensure_is_owner,
    ensure_related_to_shop,
)
from backend.application.services.time_slot import update_time_slot
from backend.application.validators.time import validate_time_slot_range
from backend.application.vars import TimeSlotId
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import (
    SQLAlchemyTimeSlotGateway,
)
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditTimeSlotCommand:
    time_slot_id: TimeSlotId
    start_time: time | None = None
    end_time: time | None = None
    label: str | None = None


class EditTimeSlotCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._time_slot_gateway = time_slot_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditTimeSlotCommand) -> None:
        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        time_slot = ensure_exists(
            await self._time_slot_gateway.load(command.time_slot_id),
            "TimeSlot",
        )
        ensure_related_to_shop(current_user, time_slot.shop_id)

        new_start_time = command.start_time or time_slot.start_time
        new_end_time = command.end_time or time_slot.end_time

        validate_time_slot_range(new_start_time, new_end_time)

        times_changed = (
            new_start_time != time_slot.start_time
            or new_end_time != time_slot.end_time
        )
        if (
            times_changed
            and await self._time_slot_gateway.exists_by_times_in_shop(
                current_user.shop_id, new_start_time, new_end_time
            )
        ):
            raise AlreadyExistsError(entity="TimeSlot")

        update_time_slot(
            time_slot,
            start_time=new_start_time,
            end_time=new_end_time,
            label=command.label,
        )

        await self._tr_manager.commit()

        logger.info("Time slot %s updated", command.time_slot_id)

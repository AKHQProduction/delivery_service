import logging
from dataclasses import dataclass
from datetime import time

from backend.application.errors import (
    AccessDeniedError,
    AlreadyExistsError,
    EntityNotFoundError,
)
from backend.application.interfaces import IdentityProvider, TransactionManager
from backend.application.interfaces.gateways.time_slot_gateway import (
    TimeSlotGateway,
)
from backend.application.policies.access import IsOwner
from backend.application.validators.time import validate_time_slot_range
from backend.application.vars import TimeSlotId

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
        idp: IdentityProvider,
        time_slot_gateway: TimeSlotGateway,
        tx: TransactionManager,
    ) -> None:
        self._idp = idp
        self._time_slot_gateway = time_slot_gateway
        self._tx = tx

    async def handle(self, command: EditTimeSlotCommand) -> None:
        current_user = await self._idp.current_user()

        if not IsOwner().is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s trying to edit time slot",
                current_user.user_id,
            )
            raise AccessDeniedError

        time_slot = await self._time_slot_gateway.load(command.time_slot_id)
        if time_slot is None:
            logger.warning("Time slot %s not found", command.time_slot_id)
            raise EntityNotFoundError(entity="TimeSlot")

        if time_slot.shop_id != current_user.shop_id:
            logger.warning(
                "Access denied for user %s trying to edit "
                "time slot %s from another shop",
                current_user.user_id,
                command.time_slot_id,
            )
            raise AccessDeniedError

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
            logger.warning(
                "Time slot already exists for shop %s with times %s-%s",
                current_user.shop_id,
                new_start_time,
                new_end_time,
            )
            raise AlreadyExistsError(entity="TimeSlot")

        time_slot.start_time = new_start_time
        time_slot.end_time = new_end_time
        if command.label is not None:
            time_slot.label = command.label

        await self._time_slot_gateway.update(time_slot)

        await self._tx.commit()

        logger.info("Time slot %s updated", command.time_slot_id)

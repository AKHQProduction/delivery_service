import logging
from dataclasses import dataclass
from datetime import time

from backend.application.errors import AccessDeniedError, AlreadyExistsError
from backend.application.interfaces.gateways.time_slot_gateway import (
    CreateTimeSlotDTO,
)
from backend.application.policies.access import IsOwner
from backend.application.validators.time import validate_time_slot_range
from backend.application.vars import TimeSlotId
from backend.infrastructure.idp import TelegramIdentityProvider
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
        idp: TelegramIdentityProvider,
        time_slot_gateway: SQLAlchemyTimeSlotGateway,
        tx: TransactionManager,
    ) -> None:
        self._idp = idp
        self._time_slot_gateway = time_slot_gateway
        self._tx = tx

    async def handle(self, command: CreateTimeSlotCommand) -> TimeSlotId:
        current_user = await self._idp.current_user()

        if not IsOwner().is_satisfied_by(current_user):
            logger.warning(
                "Access denied for user %s trying to create time slot",
                current_user.user_id,
            )
            raise AccessDeniedError

        if await self._time_slot_gateway.exists_by_times_in_shop(
            current_user.shop_id, command.start_time, command.end_time
        ):
            logger.warning(
                "Time slot already exists for shop %s with times %s-%s",
                current_user.shop_id,
                command.start_time,
                command.end_time,
            )
            raise AlreadyExistsError(entity="TimeSlot")

        time_slot_id = self._time_slot_gateway.next_id()

        await self._time_slot_gateway.create(
            CreateTimeSlotDTO(
                time_slot_id=time_slot_id,
                shop_id=current_user.shop_id,
                start_time=command.start_time,
                end_time=command.end_time,
                label=command.label,
            )
        )

        await self._tx.commit()

        logger.info(
            "Time slot %s created for shop %s",
            time_slot_id,
            current_user.shop_id,
        )

        return time_slot_id

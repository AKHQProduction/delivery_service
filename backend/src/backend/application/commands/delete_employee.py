import logging
from dataclasses import dataclass

from backend.application.policies.access import (
    ensure_is_owner,
    ensure_related_to_shop,
)
from backend.application.vars import UserId
from backend.domain.services.common import ensure_exists
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyShopGateway
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DeleteEmployeeCommand:
    user_id: UserId


class DeleteEmployeeCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        shop_gateway: SQLAlchemyShopGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._shop_gateway = shop_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: DeleteEmployeeCommand) -> None:
        logger.info(
            "Deleting employee",
            extra={"employee_user_id": command.user_id},
        )

        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        membership = ensure_exists(
            await self._shop_gateway.load_membership(command.user_id),
            "Employee",
        )
        ensure_related_to_shop(current_user, membership.shop_id)

        await self._shop_gateway.delete_membership(membership)
        await self._tr_manager.commit()

        logger.info(
            "Employee deleted successfully",
            extra={"employee_user_id": command.user_id},
        )

import logging
from dataclasses import dataclass

from backend.application.errors import FieldError
from backend.application.policies.access import (
    ensure_is_owner,
    ensure_related_to_shop,
)
from backend.application.vars import ShopRole, UserId
from backend.domain.services.common import ensure_exists
from backend.domain.services.shop import update_membership
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyShopGateway
from backend.infrastructure.transaction_manager import TransactionManager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EditEmployeeCommand:
    user_id: UserId

    new_role: ShopRole | None = None
    new_name: str | None = None

    def __post_init__(self) -> None:
        if self.new_role == ShopRole.OWNER:
            raise FieldError(
                field="new_role",
                value=self.new_role,
                acceptable_values=[ShopRole.MANAGER, ShopRole.COURIER],
            )


class EditEmployeeCommandHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        shop_gateway: SQLAlchemyShopGateway,
        tr_manager: TransactionManager,
    ) -> None:
        self._idp = idp
        self._shop_gateway = shop_gateway
        self._tr_manager = tr_manager

    async def handle(self, command: EditEmployeeCommand) -> None:
        logger.info(
            "Editing employee",
            extra={
                "employee_user_id": command.user_id,
                "new_role": command.new_role,
                "new_name": command.new_name,
            },
        )

        current_user = await self._idp.current_user()
        ensure_is_owner(current_user)

        membership = ensure_exists(
            await self._shop_gateway.load_membership(command.user_id),
            "Employee",
        )
        ensure_related_to_shop(current_user, membership.shop_id)

        new_role_id = None
        if command.new_role:
            new_role_id = await self._shop_gateway.get_role_id(
                command.new_role
            )

        update_membership(
            membership,
            name=command.new_name,
            role_id=new_role_id,
        )

        await self._tr_manager.commit()

        logger.info(
            "Employee updated successfully",
            extra={"employee_user_id": command.user_id},
        )

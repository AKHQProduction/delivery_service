import logging
from dataclasses import dataclass

from backend.application.errors import AccessDeniedError, EntityNotFoundError
from backend.application.policies.access import IsOwner, IsRelatedToShop
from backend.application.vars import UserId
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
        logger.debug(
            "Current user retrieved", extra={"user_id": current_user.user_id}
        )

        if not IsOwner().is_satisfied_by(current_user):
            logger.warning(
                "Access denied: user is not owner",
                extra={
                    "user_id": current_user.user_id,
                    "user_role": current_user.role,
                },
            )
            raise AccessDeniedError

        membership = await self._shop_gateway.load_membership(command.user_id)
        if not membership:
            logger.warning(
                "Employee not found",
                extra={"employee_user_id": command.user_id},
            )
            raise EntityNotFoundError(entity="Employee")

        logger.debug(
            "Employee found",
            extra={
                "employee_user_id": membership.user_id,
                "shop_id": membership.shop_id,
                "role": membership.role.name,
                "full_name": membership.name,
            },
        )

        if not IsRelatedToShop(shop_id=membership.shop_id).is_satisfied_by(
            current_user
        ):
            logger.warning(
                "Access denied: user not related to employee's shop",
                extra={
                    "user_id": current_user.user_id,
                    "user_shop_id": current_user.shop_id,
                    "employee_shop_id": membership.shop_id,
                },
            )
            raise AccessDeniedError

        logger.info(
            "Deleting employee from shop",
            extra={
                "employee_user_id": command.user_id,
                "shop_id": membership.shop_id,
            },
        )

        await self._shop_gateway.delete_membership(membership)
        await self._tr_manager.commit()

        logger.info(
            "Employee deleted successfully",
            extra={"employee_user_id": command.user_id},
        )

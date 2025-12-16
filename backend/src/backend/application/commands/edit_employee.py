import logging
from dataclasses import dataclass

from backend.application.errors import (
    AccessDeniedError,
    EntityNotFoundError,
    FieldError,
)
from backend.application.interfaces import (
    IdentityProvider,
    ShopGateway,
    TransactionManager,
)
from backend.application.policies.access import IsOwner, IsRelatedToShop
from backend.application.vars import ShopRole, UserId

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
        idp: IdentityProvider,
        shop_gateway: ShopGateway,
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

        employee = await self._shop_gateway.get_shop_employee(command.user_id)
        if not employee:
            logger.warning(
                "Employee not found",
                extra={"employee_user_id": command.user_id},
            )
            raise EntityNotFoundError(entity="Employee")

        logger.debug(
            "Employee found",
            extra={
                "employee_user_id": employee.user_id,
                "shop_id": employee.shop_id,
                "role": employee.role,
                "full_name": employee.full_name,
            },
        )

        if not IsRelatedToShop(shop_id=employee.shop_id).is_satisfied_by(
            current_user
        ):
            logger.warning(
                "Access denied: user not related to employee's shop",
                extra={
                    "user_id": current_user.user_id,
                    "user_shop_id": current_user.shop_id,
                    "employee_shop_id": employee.shop_id,
                },
            )
            raise AccessDeniedError

        changes = []
        if command.new_role:
            employee.role = command.new_role
            changes.append(f"role: {command.new_role}")
        if command.new_name:
            employee.full_name = command.new_name
            changes.append(f"name: {command.new_name}")

        logger.info(
            "Updating employee data",
            extra={
                "employee_user_id": command.user_id,
                "changes": ", ".join(changes),
            },
        )

        await self._shop_gateway.update_employee(employee)
        await self._tr_manager.commit()

        logger.info(
            "Employee updated successfully",
            extra={"employee_user_id": command.user_id},
        )

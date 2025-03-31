import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.identity_provider import IdentityProvider
from application.common.persistence.employee import EmployeeGateway
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import (
    validate_employee,
    validate_shop,
    validate_user,
)
from entities.employee.models import EmployeeId, EmployeeRole
from entities.employee.services import EmployeeService


@dataclass(frozen=True)
class ChangeEmployeeCommand:
    employee_id: int
    role: EmployeeRole


@dataclass
class ChangeEmployeeCommandHandler:
    identity_provider: IdentityProvider
    shop_reader: ShopGateway
    access_service: AccessService
    employee_gateway: EmployeeGateway
    employee_service: EmployeeService
    transaction_manager: TransactionManager

    async def __call__(self, data: ChangeEmployeeCommand) -> None:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_reader.load_with_identity(actor.oid)
        validate_shop(shop)

        employee = await self.employee_gateway.load_with_id(
            EmployeeId(data.employee_id)
        )
        validate_employee(employee)

        await self.access_service.ensure_can_edit_employee(actor.oid, shop.oid)

        self.employee_service.change_employee_role(employee, data.role)

        await self.transaction_manager.commit()

        logging.info(
            "Edit employee with user_id=%s",
            employee.user_id,
        )

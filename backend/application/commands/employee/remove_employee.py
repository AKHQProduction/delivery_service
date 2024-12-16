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
from entities.employee.models import EmployeeId
from entities.employee.services import EmployeeService


@dataclass(frozen=True)
class RemoveEmployeeCommand:
    employee_id: int


@dataclass
class RemoveEmployeeCommandHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    access_service: AccessService
    employee_gateway: EmployeeGateway
    employee_service: EmployeeService
    transaction_manager: TransactionManager

    async def __call__(self, data: RemoveEmployeeCommand) -> None:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        employee_id = EmployeeId(data.employee_id)
        shop_id = shop.oid

        await self.access_service.ensure_can_edit_employee(actor.oid, shop_id)

        employee = await self.employee_gateway.load_with_id(employee_id)
        validate_employee(employee)

        await self.employee_service.remove_from_employee(employee)

        await self.transaction_manager.commit()

        logging.info(
            "RemoveEmployee: employee id=%s remove from employees", employee_id
        )

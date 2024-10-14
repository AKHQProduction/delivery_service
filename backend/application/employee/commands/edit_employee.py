import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.employee.errors import EmployeeNotFoundError
from application.employee.gateway import EmployeeGateway
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopReader
from application.user.errors import UserNotFoundError
from entities.employee.models import EmployeeId, EmployeeRole


@dataclass(frozen=True)
class ChangeEmployeeInputData:
    employee_id: int
    role: EmployeeRole


@dataclass
class ChangeEmployee:
    identity_provider: IdentityProvider
    shop_reader: ShopReader
    access_service: AccessService
    employee_gateway: EmployeeGateway
    commiter: Commiter

    async def __call__(self, data: ChangeEmployeeInputData) -> None:
        actor = await self.identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()

        shop = await self.shop_reader.by_identity(actor.user_id)
        if not shop:
            raise UserNotHaveShopError(actor.user_id)

        employee = await self.employee_gateway.by_id(
            EmployeeId(data.employee_id)
        )
        if not employee:
            raise EmployeeNotFoundError(data.employee_id)

        await self.access_service.ensure_can_edit_employee(
            actor.user_id, shop.shop_id, employee
        )

        employee.role = data.role

        await self.commiter.commit()

        logging.info(
            "Edit employee with user_id=%s",
            employee.user_id,
        )

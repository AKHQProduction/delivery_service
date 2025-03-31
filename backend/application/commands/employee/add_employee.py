import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.errors.employee import EmployeeAlreadyExistsError
from application.common.identity_provider import IdentityProvider
from application.common.persistence.employee import EmployeeGateway
from application.common.persistence.shop import ShopGateway
from application.common.persistence.user import UserGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import validate_shop, validate_user
from entities.employee.models import EmployeeRole
from entities.employee.services import EmployeeService
from entities.user.models import UserId


@dataclass(frozen=True)
class AddEmployeeCommand:
    user_id: int
    role: EmployeeRole


@dataclass
class AddEmployeeCommandHandler:
    identity_provider: IdentityProvider
    employee_gateway: EmployeeGateway
    employee_service: EmployeeService
    shop_gateway: ShopGateway
    user_gateway: UserGateway
    access_service: AccessService
    transaction_manager: TransactionManager

    async def __call__(self, data: AddEmployeeCommand) -> None:
        user_id = UserId(data.user_id)

        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        user_to_add = await self.user_gateway.load_with_id(user_id)
        validate_user(user_to_add)

        await self.access_service.ensure_can_create_employee(
            actor.oid, shop.oid
        )

        if await self.employee_gateway.is_exist(user_id):
            raise EmployeeAlreadyExistsError(user_id)

        self.employee_service.add_employee(
            shop.oid, user_to_add.oid, data.role
        )

        await self.transaction_manager.commit()

        logging.info(
            "AddEmployee: with user_id=%s add to employees", data.user_id
        )

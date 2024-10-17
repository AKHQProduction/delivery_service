import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.employee.gateway import EmployeeGateway
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopGateway
from application.user.errors import UserNotFoundError
from entities.employee.models import EmployeeId


@dataclass(frozen=True)
class RemoveEmployeeInputData:
    employee_id: int


class RemoveEmployee(Interactor[RemoveEmployeeInputData, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        shop_reader: ShopGateway,
        access_service: AccessService,
        employee_gateway: EmployeeGateway,
        commiter: Commiter,
    ) -> None:
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._access_service = access_service
        self._employee_gateway = employee_gateway
        self._commiter = commiter

    async def __call__(self, data: RemoveEmployeeInputData) -> None:
        actor = await self._identity_provider.get_user()
        if not actor:
            raise UserNotFoundError()

        shop = await self._shop_reader.by_identity(actor.user_id)
        if not shop:
            raise UserNotHaveShopError(actor.user_id)

        employee_id = EmployeeId(data.employee_id)

        employee = await self._employee_gateway.by_id(employee_id)

        shop_id = shop.shop_id

        await self._access_service.ensure_can_edit_employee(
            actor.user_id, shop_id, employee
        )

        await self._employee_gateway.delete(employee_id)

        await self._commiter.commit()

        logging.info(
            "RemoveEmployee: employee id=%s remove from employees", employee_id
        )

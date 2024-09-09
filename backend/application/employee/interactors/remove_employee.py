import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.employee.gateway import EmployeeSaver
from entities.employee.models import EmployeeId
from entities.shop.models import ShopId


@dataclass(frozen=True)
class RemoveEmployeeInputData:
    employee_id: int
    shop_id: int


class RemoveEmployee(Interactor[RemoveEmployeeInputData, None]):
    def __init__(
            self,
            identity_provider: IdentityProvider,
            access_service: AccessService,
            employee_saver: EmployeeSaver,
            commiter: Commiter
    ) -> None:
        self._identity_provider = identity_provider
        self._access_service = access_service
        self._employee_saver = employee_saver
        self._commiter = commiter

    async def __call__(self, data: RemoveEmployeeInputData) -> None:
        employee_id = EmployeeId(data.employee_id)
        shop_id = ShopId(data.shop_id)

        await self._access_service.ensure_can_edit_employee(shop_id)

        await self._employee_saver.delete(employee_id)

        await self._commiter.commit()

        logging.info(
                f"RemoveEmployee: employee={employee_id} remove from employees"
        )

import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.interactor import Interactor
from application.employee.gateway import EmployeeSaver
from application.shop.errors import ShopIsNotExistError
from application.shop.gateway import ShopReader
from application.user.errors import UserIsNotExistError
from application.user.gateway import UserReader

from entities.employee.models import Employee, EmployeeRole
from entities.shop.models import ShopId
from entities.user.models import UserId


@dataclass(frozen=True)
class AddEmployeeRequestData:
    user_id: int
    shop_id: int
    role: EmployeeRole


class AddEmployee(Interactor[AddEmployeeRequestData, None]):
    def __init__(
            self,
            employee_saver: EmployeeSaver,
            shop_reader: ShopReader,
            user_reader: UserReader,
            access_service: AccessService,
            commiter: Commiter
    ):
        self._employee_saver = employee_saver
        self._shop_reader = shop_reader
        self._user_reader = user_reader
        self._access_service = access_service
        self._commiter = commiter

    async def __call__(self, data: AddEmployeeRequestData) -> None:
        user_id = UserId(data.user_id)
        shop_id = ShopId(data.shop_id)

        user = await self._user_reader.by_id(user_id)

        if not user:
            raise UserIsNotExistError(data.user_id)

        shop = await self._shop_reader.by_id(shop_id)

        if not shop:
            raise ShopIsNotExistError(data.shop_id)

        await self._access_service.ensure_can_create_employee(shop_id)

        await self._employee_saver.save(
                Employee(
                        employee_id=None,
                        user_id=user_id,
                        shop_id=shop_id,
                        role=data.role
                )
        )

        await self._commiter.commit()

        logging.info(f"AddEmployee: user={data.user_id} add to employees")

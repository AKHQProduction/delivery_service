import logging
from dataclasses import dataclass

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.employee.errors import EmployeeAlreadyExistError
from application.employee.gateway import EmployeeGateway
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopGateway
from application.user.errors import UserNotFoundError
from application.user.gateway import UserReader
from entities.employee.models import Employee, EmployeeRole
from entities.user.models import UserId


@dataclass(frozen=True)
class AddEmployeeInputData:
    user_id: int
    role: EmployeeRole


class AddEmployee(Interactor[AddEmployeeInputData, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        employee_saver: EmployeeGateway,
        shop_reader: ShopGateway,
        user_reader: UserReader,
        access_service: AccessService,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._employee_saver = employee_saver
        self._shop_reader = shop_reader
        self._user_reader = user_reader
        self._access_service = access_service
        self._commiter = commiter

    async def __call__(self, data: AddEmployeeInputData) -> None:
        user_id = UserId(data.user_id)

        employee = await self._identity_provider.get_user()
        if not employee:
            raise UserNotFoundError()

        shop = await self._shop_reader.by_identity(employee.user_id)
        if not shop:
            raise UserNotHaveShopError(employee.user_id)

        user = await self._user_reader.by_id(user_id)
        if not user:
            raise UserNotFoundError(data.user_id)

        await self._access_service.ensure_can_create_employee(
            employee.user_id, shop.shop_id
        )

        if await self._employee_saver.is_exist(user_id):
            raise EmployeeAlreadyExistError(user_id)

        await self._employee_saver.save(
            Employee(
                employee_id=None,
                user_id=user_id,
                shop_id=shop.shop_id,
                role=data.role,
            ),
        )

        await self._commiter.commit()

        logging.info(
            "AddEmployee: with user_id=%s add to employees", data.user_id
        )

import pytest

from application.common.access_service import AccessService
from application.employee.errors import EmployeeAlreadyExistError
from application.employee.interactors.add_employee import (
    AddEmployee,
    AddEmployeeInputData,
)
from application.errors.access import AccessDeniedError
from application.shop.errors import UserNotHaveShopError
from application.user.errors import UserIsNotExistError
from entities.employee.models import EmployeeRole
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.gateways.employee import FakeEmployeeGateway
from tests.mocks.gateways.shop import FakeShopGateway
from tests.mocks.gateways.user import FakeUserGateway


@pytest.mark.application
@pytest.mark.employee
@pytest.mark.parametrize(
    ["user_id", "user_id_to_add", "exc_class"],
    [
        (1, 2, None),
        (4, 2, UserIsNotExistError),
        (1, 1, EmployeeAlreadyExistError),
        (2, 4, UserNotHaveShopError),
        (1, 4, UserIsNotExistError),
        (3, 2, AccessDeniedError),
    ],
)
async def test_add_employee(
    identity_provider: FakeIdentityProvider,
    employee_gateway: FakeEmployeeGateway,
    user_gateway: FakeUserGateway,
    shop_gateway: FakeShopGateway,
    commiter: FakeCommiter,
    access_service: AccessService,
    user_id: UserId,
    user_id_to_add: int,
    exc_class,
) -> None:
    action = AddEmployee(
        identity_provider=identity_provider,
        access_service=access_service,
        employee_saver=employee_gateway,
        user_reader=user_gateway,
        shop_reader=shop_gateway,
        commiter=commiter,
    )

    input_data = AddEmployeeInputData(
        user_id=user_id_to_add, role=EmployeeRole.MANAGER
    )

    coro = action(input_data)

    if exc_class:
        with pytest.raises(exc_class):
            await coro

        assert not employee_gateway.saved
        assert not commiter.commited

    else:
        output_data = await coro

        assert not output_data

        assert employee_gateway.saved
        assert commiter.commited

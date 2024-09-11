import pytest

from application.common.access_service import AccessService
from application.employee.errors import EmployeeIsNotExistError
from application.employee.interactors.remove_employee import (
    RemoveEmployee,
    RemoveEmployeeInputData
)
from application.errors.access import AccessDeniedError
from application.shop.errors import UserNotHaveShopError
from application.user.errors import UserIsNotExistError
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.gateways.employee import FakeEmployeeGateway
from tests.mocks.gateways.shop import FakeShopGateway


@pytest.mark.application
@pytest.mark.employee
@pytest.mark.parametrize(
        ["user_id", "employee_id_to_del", "exc_class"],
        [
            (1, 2, None),
            (4, 2, UserIsNotExistError),
            (2, 4, UserNotHaveShopError),
            (3, 2, AccessDeniedError),
            (1, 3, EmployeeIsNotExistError)
        ]
)
async def test_remove_employee(
        identity_provider: FakeIdentityProvider,
        employee_gateway: FakeEmployeeGateway,
        shop_gateway: FakeShopGateway,
        commiter: FakeCommiter,
        user_id: UserId,
        employee_id_to_del: int,
        exc_class
) -> None:
    access_service = AccessService(
            employee_reader=employee_gateway,
            identity_provider=identity_provider
    )

    action = RemoveEmployee(
            identity_provider=identity_provider,
            access_service=access_service,
            employee_saver=employee_gateway,
            shop_reader=shop_gateway,
            commiter=commiter
    )

    input_data = RemoveEmployeeInputData(
            employee_id=employee_id_to_del
    )

    coro = action(input_data)

    if exc_class:
        with pytest.raises(exc_class):
            await coro

            assert not commiter.commited
            assert not employee_gateway.deleted

    else:
        output_data = await coro

        assert not output_data
        assert commiter.commited
        assert employee_gateway.deleted

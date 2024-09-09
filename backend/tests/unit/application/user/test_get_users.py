import pytest

from application.common.request_data import Pagination
from application.user.gateway import GetUsersFilters
from application.user.interactors.get_users import (
    GetUsers,
    GetUsersInputData,
    GetUsersOutputData
)
from entities.user.models import User
from tests.mocks.gateways.user import FakeUserGateway


@pytest.mark.application
@pytest.mark.user
async def test_get_users(user_gateway: FakeUserGateway, user: User) -> None:
    interactor = GetUsers(user_gateway)

    input_data = GetUsersInputData(Pagination(), GetUsersFilters())

    output_data = await interactor(input_data)

    assert isinstance(output_data, GetUsersOutputData)
    assert output_data.total == 1
    assert isinstance(output_data.users, list)
    assert user in output_data.users

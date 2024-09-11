import pytest

from application.common.request_data import Pagination
from application.user.gateway import GetUsersFilters
from application.user.interactors.get_users import (
    GetUsers,
    GetUsersInputData,
    GetUsersOutputData
)
from tests.mocks.gateways.user import FakeUserGateway


@pytest.mark.application
@pytest.mark.user
async def test_get_users(user_gateway: FakeUserGateway) -> None:
    action = GetUsers(user_reader=user_gateway)

    input_data = GetUsersInputData(
            pagination=Pagination(),
            filters=GetUsersFilters()
    )

    output_data = await action(input_data)

    assert output_data
    assert isinstance(output_data, GetUsersOutputData)

    assert output_data.users == list(user_gateway.users.values())
    assert output_data.total == len(list(user_gateway.users.values()))

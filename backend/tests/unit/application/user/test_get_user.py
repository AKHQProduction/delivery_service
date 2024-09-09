import pytest

from application.user.errors import UserIsNotExistError
from application.user.interactors.get_user import (
    GetUser,
    GetUserInputData,
    GetUserOutputData
)
from entities.user.models import UserId
from tests.mocks.gateways.user import FakeUserGateway
from tests.unit.conftest import user_fullname


@pytest.mark.application
@pytest.mark.user
async def test_successfully_get_user(
        user_gateway: FakeUserGateway,
        user_id: UserId,
        user_fullname: str,
) -> None:
    interactor = GetUser(
            user_reader=user_gateway
    )

    input_data = GetUserInputData(user_id)

    output_data = await interactor(input_data)

    assert isinstance(output_data, GetUserOutputData)
    assert output_data.user_id == user_id
    assert output_data.full_name == user_fullname
    assert output_data.username is None


@pytest.mark.application
@pytest.mark.user
async def test_failed_get_user(
        user_gateway: FakeUserGateway
) -> None:
    interactor = GetUser(
            user_reader=user_gateway
    )

    input_data = GetUserInputData(2)

    with pytest.raises(UserIsNotExistError):
        await interactor(input_data)

import pytest

from application.user.errors import UserIsNotExistError
from application.user.interactors.get_user import (
    GetUser,
    GetUserInputData,
    GetUserOutputData
)
from entities.user.models import UserId
from tests.mocks.gateways.user import FakeUserGateway


@pytest.mark.application
@pytest.mark.user
@pytest.mark.parametrize(
        ["user_id", "exc_class"],
        [
            (1, None),
            (4, UserIsNotExistError)
        ]
)
async def test_get_user(
        user_gateway: FakeUserGateway,
        user_id: UserId,
        exc_class
) -> None:
    action = GetUser(user_reader=user_gateway)

    input_data = GetUserInputData(
            user_id=user_id
    )

    if exc_class:
        with pytest.raises(exc_class):
            await action(input_data)
    else:
        output_data = await action(input_data)

        assert output_data
        assert isinstance(output_data, GetUserOutputData)

        assert output_data.user_id == user_id

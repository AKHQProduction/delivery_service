import pytest

from application.user.interactors.bot_start import BotStart, BotStartInputData
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.gateways.user import FakeUserGateway


@pytest.mark.application
@pytest.mark.user
@pytest.mark.parametrize(
        ["user_id"],
        [
            (1,),
            (2,)
        ]
)
async def test_bot_start_with_already_created_user(
        user_gateway: FakeUserGateway,
        commiter: FakeCommiter,
        identity_provider: FakeIdentityProvider,
        user_id: UserId
) -> None:
    action = BotStart(
            user_reader=user_gateway,
            user_saver=user_gateway,
            commiter=commiter,
            identity_provider=identity_provider
    )

    input_data = BotStartInputData(
            user_id=user_id,
            full_name="Test Test Test"
    )

    output_data = await action(input_data)

    assert output_data
    assert isinstance(output_data, int)
    assert not user_gateway.saved
    assert output_data == user_id


@pytest.mark.application
@pytest.mark.user
@pytest.mark.parametrize(
        ["user_id"],
        [
            (3,),
            (4,)
        ]
)
async def test_bot_start_when_create_new_user(
        user_gateway: FakeUserGateway,
        commiter: FakeCommiter,
        identity_provider: FakeIdentityProvider,
        user_id: UserId
) -> None:
    action = BotStart(
            user_reader=user_gateway,
            user_saver=user_gateway,
            commiter=commiter,
            identity_provider=identity_provider
    )

    input_data = BotStartInputData(
            user_id=user_id,
            full_name="Test Test Test"
    )

    output_data = await action(input_data)

    assert output_data
    assert isinstance(output_data, int)
    assert user_gateway.saved
    assert output_data == user_id

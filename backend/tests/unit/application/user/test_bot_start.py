import pytest

from application.user.interactors.bot_start import (
    BotStart,
    BotStartInputData
)
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.gateways.user import FakeUserGateway
from tests.unit.conftest import user_fullname


@pytest.mark.application
@pytest.mark.user
async def test_bot_start(
        user_gateway: FakeUserGateway,
        identity_provider: FakeIdentityProvider,
        commiter: FakeCommiter,
        user_id: UserId,
        user_fullname: str
) -> None:
    interactor = BotStart(
            user_reader=user_gateway,
            user_saver=user_gateway,
            identity_provider=identity_provider,
            commiter=commiter
    )

    input_data = BotStartInputData(
            user_id=user_id,
            full_name=user_fullname
    )

    output_data = await interactor(input_data)

    assert output_data
    assert isinstance(output_data, int)

    assert not user_gateway.saved
    assert output_data == user_gateway.user.user_id
    assert user_id == output_data

    assert commiter.commited


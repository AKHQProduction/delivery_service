import pytest

from application.user.interactors.admin_bot_start import (
    AdminBotStart,
    AdminBotStartInputData,
    AdminBotStartOutputData,
)
from entities.user.models import UserId
from tests.mocks.common.commiter import FakeCommiter
from tests.mocks.common.identity_provider import FakeIdentityProvider
from tests.mocks.gateways.profile import FakeProfileGateway
from tests.mocks.gateways.user import FakeUserGateway


@pytest.mark.application
@pytest.mark.user
@pytest.mark.parametrize(["user_id"], [(1,), (2,)])
async def test_bot_start_with_already_created_user(
    user_gateway: FakeUserGateway,
    commiter: FakeCommiter,
    identity_provider: FakeIdentityProvider,
    profile_gateway: FakeProfileGateway,
    user_id: UserId,
) -> None:
    action = AdminBotStart(
        user_reader=user_gateway,
        user_saver=user_gateway,
        commiter=commiter,
        identity_provider=identity_provider,
        profile_saver=profile_gateway,
    )

    input_data = AdminBotStartInputData(
        user_id=user_id, full_name="Test Test Test", username="TestUsername"
    )

    output_data = await action(input_data)

    assert output_data
    assert isinstance(output_data, AdminBotStartOutputData)
    assert not user_gateway.saved
    assert not commiter.commited


@pytest.mark.application
@pytest.mark.user
@pytest.mark.parametrize(["user_id"], [(4,), (5,)])
async def test_bot_start_when_create_new_user(
    user_gateway: FakeUserGateway,
    commiter: FakeCommiter,
    identity_provider: FakeIdentityProvider,
    profile_gateway: FakeProfileGateway,
    user_id: UserId,
) -> None:
    action = AdminBotStart(
        user_reader=user_gateway,
        user_saver=user_gateway,
        commiter=commiter,
        identity_provider=identity_provider,
        profile_saver=profile_gateway,
    )

    input_data = AdminBotStartInputData(
        user_id=user_id, full_name="Test Test Test", username="TestUsername"
    )

    output_data = await action(input_data)

    assert output_data
    assert isinstance(output_data, AdminBotStartOutputData)
    assert user_gateway.saved
    assert commiter.commited

from unittest.mock import create_autospec

import pytest

from delivery_service.application.commands.main_bot_start import (
    MainBotStart,
    MainBotStartHandler,
)
from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.application.ports.view_manager import ViewManager
from delivery_service.core.users.factory import (
    TelegramContactsData,
    UserFactory,
)
from delivery_service.core.users.repository import UserRepository


@pytest.mark.parametrize(
    ["user_is_already_exists"],
    [(True,), (False,)],
)
async def test_main_bot_start(
    service_user_factory: UserFactory, user_is_already_exists: bool
) -> None:
    mock_user_repository = create_autospec(UserRepository, instance=True)
    mock_user_repository.exists.return_value = user_is_already_exists
    mock_user_factory = create_autospec(UserFactory, instance=True)
    mock_view_manager = create_autospec(ViewManager, instance=True)
    mock_transaction_manager = create_autospec(
        TransactionManager, instance=True
    )

    handler = MainBotStartHandler(
        user_repository=mock_user_repository,
        user_factory=mock_user_factory,
        view_manager=mock_view_manager,
        transaction_manager=mock_transaction_manager,
    )
    request_data = MainBotStart(
        full_name="Kevin Rudolf",
        telegram_data=TelegramContactsData(
            telegram_id=1234567890, telegram_username="@Kevin_Rudolf"
        ),
    )
    response_data = await handler.handle(request_data)

    assert response_data is None
    mock_user_repository.exists.assert_called_once_with(
        request_data.telegram_data
    )
    mock_view_manager.send_greeting_message.assert_called_once()

    if not user_is_already_exists:
        mock_user_factory.create_user.assert_called_once_with(
            full_name=request_data.full_name,
            telegram_contacts_data=request_data.telegram_data,
        )
        mock_user_repository.add.assert_called_once()
        mock_transaction_manager.commit.assert_called_once()
    else:
        mock_user_factory.create_user.assert_not_called()
        mock_user_repository.add.assert_not_called()
        mock_transaction_manager.commit.assert_not_called()

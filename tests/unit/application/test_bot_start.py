from unittest.mock import create_autospec

from delivery_service.application.commands.main_bot_start import (
    MainBotStartHandler,
    MainBotStartRequest,
)
from delivery_service.application.ports.transaction_manager import (
    TransactionManager,
)
from delivery_service.application.ports.view_manager import ViewManager
from delivery_service.core.users.errors import UserAlreadyExistsError
from delivery_service.core.users.factory import (
    TelegramContactsData,
    UserFactory,
)
from delivery_service.core.users.repository import UserRepository


async def test_main_bot_start() -> None:
    mock_user_repository = create_autospec(UserRepository, instance=True)
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
    request_data = MainBotStartRequest(
        full_name="Kevin Rudolf",
        telegram_data=TelegramContactsData(
            telegram_id=1, telegram_username="@Kevin"
        ),
    )

    response_data = await handler.handle(request_data)

    assert response_data is None
    mock_user_factory.create_user.assert_called_once()
    mock_user_repository.add.assert_called_once()
    mock_view_manager.send_greeting_message.assert_called_once()
    mock_transaction_manager.commit.assert_called_once()


async def test_main_bot_start_when_user_already_exists() -> None:
    mock_user_repository = create_autospec(UserRepository, instance=True)
    mock_user_factory = create_autospec(UserFactory, instance=True)
    mock_view_manager = create_autospec(ViewManager, instance=True)
    mock_transaction_manager = create_autospec(
        TransactionManager, instance=True
    )

    mock_user_factory.create_user.side_effect = UserAlreadyExistsError(1)

    handler = MainBotStartHandler(
        user_repository=mock_user_repository,
        user_factory=mock_user_factory,
        view_manager=mock_view_manager,
        transaction_manager=mock_transaction_manager,
    )
    request_data = MainBotStartRequest(
        full_name="Kevin Rudolf",
        telegram_data=TelegramContactsData(
            telegram_id=1, telegram_username="@Kevin"
        ),
    )

    response_data = await handler.handle(request_data)

    assert response_data is None

    mock_user_factory.create_user.assert_called_once()
    mock_view_manager.send_greeting_message.assert_called_once()

    mock_user_repository.add.assert_not_called()
    mock_transaction_manager.commit.assert_not_called()

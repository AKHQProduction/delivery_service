import uuid
from typing import Type
from unittest.mock import create_autospec

import pytest

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.shared.tg_contacts import TelegramContacts
from delivery_service.core.users.errors import (
    FullNameTooLongError,
    InvalidFullNameError,
    InvalidTelegramUsernameError,
    TelegramIDMustBePositiveError,
)
from delivery_service.core.users.factory import (
    TelegramContactsData,
)
from delivery_service.core.users.repository import UserRepository
from delivery_service.core.users.user import (
    User,
    UserID,
)
from delivery_service.infrastructure.factories.user_factory import (
    UserFactoryImpl,
)

FAKE_UUID = uuid.UUID("0195381b-8549-708d-b29b-a923d7870d78")


@pytest.mark.parametrize(
    ["full_name", "telegram_contacts_data", "exception"],
    [
        (
            "Kevin Rudolf",
            TelegramContactsData(telegram_id=1, telegram_username=None),
            None,
        ),
        (
            "Kevin Rudolf",
            TelegramContactsData(telegram_id=1, telegram_username="@abc"),
            None,
        ),
        ("", None, InvalidFullNameError),
        ("A" * 129, None, FullNameTooLongError),
        (
            "Kevin Rudolf",
            TelegramContactsData(telegram_id=-1, telegram_username="@abc"),
            TelegramIDMustBePositiveError,
        ),
        (
            "Kevin Rudolf",
            TelegramContactsData(telegram_id=1, telegram_username=""),
            InvalidTelegramUsernameError,
        ),
        (
            "Kevin Rudolf",
            TelegramContactsData(telegram_id=1, telegram_username="@" * 129),
            InvalidTelegramUsernameError,
        ),
    ],
)
async def test_create_user(
    full_name: str,
    telegram_contacts_data: TelegramContactsData,
    exception: Type[Exception] | None,
) -> None:
    mock_id_generator = create_autospec(IDGenerator, instance=True)
    mock_id_generator.generate_service_client_id.return_value = FAKE_UUID
    mock_user_repository = create_autospec(UserRepository, instance=True)
    mock_user_repository.exists.return_value = False

    service_client_factory = UserFactoryImpl(
        id_generator=mock_id_generator, user_repository=mock_user_repository
    )

    coro = service_client_factory.create_user(
        full_name=full_name,
        telegram_contacts_data=telegram_contacts_data,
    )

    if exception:
        with pytest.raises(exception):
            await coro
    else:
        new_user = await coro

        assert isinstance(new_user, User)
        assert new_user.full_name == full_name
        assert new_user.entity_id == FAKE_UUID

        if telegram_contacts_data is not None:
            assert new_user.telegram_contacts is not None
            assert (
                new_user.telegram_contacts.telegram_id
                == telegram_contacts_data.telegram_id
            )
            assert (
                new_user.telegram_contacts.telegram_username
                == telegram_contacts_data.telegram_username
            )
        else:
            assert new_user.telegram_contacts is None

        mock_id_generator.generate_service_client_id.assert_called_once()
        mock_user_repository.exists.assert_called_once_with(
            telegram_contacts_data
        )


async def test_create_several_users() -> None:
    first_user = User(
        entity_id=UserID(FAKE_UUID),
        full_name="Kevin Rudolf",
        telegram_contacts=TelegramContacts(
            telegram_id=1, telegram_username="@Kevin"
        ),
    )
    second_user = User(
        entity_id=UserID(uuid.UUID("01953cdd-6dc1-797c-8029-170692b243cf")),
        full_name="Kevin Rudolf",
        telegram_contacts=TelegramContacts(
            telegram_id=1, telegram_username="@Kevin"
        ),
    )

    assert first_user != second_user
    assert first_user.entity_id != second_user.entity_id


def test_successfully_edit_telegram_contacts() -> None:
    service_client = User(
        entity_id=UserID(FAKE_UUID),
        full_name="Kevin Rudolf",
        telegram_contacts=TelegramContacts(
            telegram_id=1, telegram_username="@Kevin"
        ),
    )
    new_telegram_id = 2
    new_telegram_username = "@TestUsername"

    service_client.edit_telegram_contacts(
        new_telegram_id, new_telegram_username
    )

    assert service_client.telegram_contacts
    assert service_client.telegram_contacts.telegram_id == new_telegram_id
    assert (
        service_client.telegram_contacts.telegram_username
        == new_telegram_username
    )

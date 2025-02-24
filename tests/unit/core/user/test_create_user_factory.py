import uuid
from typing import Type
from unittest.mock import create_autospec

import pytest

from delivery_service.application.ports.id_generator import IDGenerator
from delivery_service.core.users.errors import (
    FullNameTooLongError,
    InvalidFullNameError,
    InvalidTelegramUsernameError,
    TelegramIDMustBePositiveError,
)
from delivery_service.core.users.factory import (
    ServiceClientFactory,
    TelegramContactsData,
)
from delivery_service.core.users.service_client import (
    ServiceClient,
    ServiceClientID,
)
from delivery_service.infrastructure.factories.service_client_factory import (
    ServiceClientFactoryImpl,
)

FAKE_UUID = uuid.UUID("0195381b-8549-708d-b29b-a923d7870d78")


@pytest.mark.parametrize(
    ["full_name", "telegram_contacts_data", "exception"],
    [
        ("Kevin Rudolf", None, None),
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
def test_create_service_client(
    full_name: str,
    telegram_contacts_data: TelegramContactsData | None,
    exception: Type[Exception] | None,
) -> None:
    mock_id_generator = create_autospec(IDGenerator, instance=True)
    mock_id_generator.generate_service_client_id.return_value = FAKE_UUID

    service_client_factory = ServiceClientFactoryImpl(
        id_generator=mock_id_generator
    )

    if exception:
        with pytest.raises(exception):
            service_client_factory.create_service_user(
                full_name=full_name,
                telegram_contacts_data=telegram_contacts_data,
            )
    else:
        new_user = service_client_factory.create_service_user(
            full_name=full_name, telegram_contacts_data=telegram_contacts_data
        )
        assert isinstance(new_user, ServiceClient)
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


def test_create_several_users(
    service_client_factory: ServiceClientFactory,
) -> None:
    first_user = service_client_factory.create_service_user(
        full_name="First_user", telegram_contacts_data=None
    )
    second_user = service_client_factory.create_service_user(
        full_name="Second user", telegram_contacts_data=None
    )

    assert first_user != second_user
    assert first_user._entity_id != second_user._entity_id


def test_successfully_edit_telegram_contacts() -> None:
    service_client = ServiceClient(
        entity_id=ServiceClientID(uuid.uuid4()), full_name="Kevin Rudolf"
    )
    new_telegram_id = 1
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

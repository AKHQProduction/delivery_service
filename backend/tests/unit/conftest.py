import random

import pytest

from entities.user.models import User, UserId


@pytest.fixture
def user_id() -> UserId:
    return UserId(1)


@pytest.fixture
def another_user_id() -> int:
    return random.randint(1, 100)


@pytest.fixture
def user_fullname() -> str:
    return "Testov Test Testovich"


@pytest.fixture
def user(user_id: UserId, user_fullname: user_fullname) -> User:
    return User(
            user_id=user_id,
            full_name=user_fullname
    )

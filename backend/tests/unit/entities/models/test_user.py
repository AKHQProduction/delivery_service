import pytest

from entities.user.models import User


@pytest.mark.entities
@pytest.mark.user
def test_create_user(user: User):
    assert user.user_id == 1
    assert user.full_name == "Testov Test Testovich"
    assert user.is_active

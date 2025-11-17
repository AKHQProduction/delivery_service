import uuid

import pytest

from backend.application.interfaces.idp import CurrentUserDTO
from backend.application.policies.access import (
    IsManager,
    IsOwner,
    can_shop_manage_policy,
)
from backend.application.vars import ShopId, ShopRole, UserId


def test_owner_policy_return_true_if_user_is_owner() -> None:
    user_dto = CurrentUserDTO(
        user_id=UserId(uuid.uuid4()),
        role=ShopRole.OWNER,
        shop_id=ShopId(uuid.uuid4()),
    )
    policy = IsOwner()

    assert policy.is_satisfied_by(user_dto)


def test_owner_policy_return_false_if_user_in_not_owner() -> None:
    user_dto = CurrentUserDTO(
        user_id=UserId(uuid.uuid4()),
        role=ShopRole.MANAGER,
        shop_id=ShopId(uuid.uuid4()),
    )
    policy = IsOwner()

    assert not policy.is_satisfied_by(user_dto)


def test_manager_policy_return_true_if_user_is_manager() -> None:
    user_dto = CurrentUserDTO(
        user_id=UserId(uuid.uuid4()),
        role=ShopRole.MANAGER,
        shop_id=ShopId(uuid.uuid4()),
    )
    policy = IsManager()

    assert policy.is_satisfied_by(user_dto)


def test_manager_policy_return_false_if_user_in_not_manager() -> None:
    user_dto = CurrentUserDTO(
        shop_id=ShopId(uuid.uuid4()),
        user_id=UserId(uuid.uuid4()),
        role=ShopRole.OWNER,
    )
    policy = IsManager()

    assert not policy.is_satisfied_by(user_dto)


@pytest.mark.parametrize("role", (ShopRole.OWNER, ShopRole.MANAGER))
def test_can_shop_manage_policy_return_true_if_user_role_in_manage_scope(
    role: ShopRole,
) -> None:
    dto = CurrentUserDTO(
        user_id=UserId(uuid.uuid4()),
        role=ShopRole.OWNER,
        shop_id=ShopId(uuid.uuid4()),
    )

    assert can_shop_manage_policy.is_satisfied_by(dto)


def test_can_shop_manage_policy_return_false_if_user_not_admin() -> None:
    dto = CurrentUserDTO(
        user_id=UserId(uuid.uuid4()),
        role=ShopRole.COURIER,
        shop_id=ShopId(uuid.uuid4()),
    )

    assert not can_shop_manage_policy.is_satisfied_by(dto)

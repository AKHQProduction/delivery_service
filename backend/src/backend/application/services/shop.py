from backend.application.vars import ShopId, UserId
from backend.infrastructure.persistence.tables import Shop, ShopMembership


def create_shop(
    *,
    shop_id: ShopId,
    name: str,
    owner_user_id: UserId,
    owner_name: str,
    owner_role_id: int,
) -> Shop:
    return Shop(
        id=shop_id,
        name=name,
        memberships=[
            ShopMembership(
                user_id=owner_user_id,
                role_id=owner_role_id,
                name=owner_name,
            )
        ],
    )


def create_membership(
    *,
    user_id: UserId,
    shop_id: ShopId,
    role_id: int,
    name: str,
) -> ShopMembership:
    return ShopMembership(
        user_id=user_id,
        shop_id=shop_id,
        role_id=role_id,
        name=name,
    )


def update_membership(
    membership: ShopMembership,
    *,
    name: str | None = None,
    role_id: int | None = None,
) -> None:
    if name is not None:
        membership.name = name
    if role_id is not None:
        membership.role_id = role_id

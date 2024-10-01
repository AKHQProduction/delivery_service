from entities.profile.models import Profile
from entities.profile.value_objects import UserAddress
from entities.shop.models import ShopId
from entities.user.models import UserId


def create_user_profile(
    shop_id: ShopId | None,
    full_name: str,
    address: UserAddress | None,
    user_id: UserId | None,
) -> Profile:
    return Profile(
        profile_id=None,
        full_name=full_name,
        shop_id=shop_id,
        user_address=address,
        user_id=user_id,
    )

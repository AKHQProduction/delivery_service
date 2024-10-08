from application.profile.gateway import ProfileReader, ProfileSaver
from entities.profile.models import Profile, ProfileId
from entities.shop.models import ShopId
from entities.user.models import UserId


class FakeProfileGateway(ProfileSaver, ProfileReader):
    def __init__(self):
        self.saver = False

    async def save(self, profile: Profile) -> None:
        self.saver = True

    async def by_identity(
        self, user_id: UserId, shop_id: ShopId | None = None
    ) -> Profile | None:
        return Profile(profile_id=ProfileId(1), shop_id=None)

from application.profile.gateway import ProfileReader, ProfileSaver
from entities.profile.models import Profile, ProfileId
from entities.user.models import UserId


class FakeProfileGateway(ProfileSaver, ProfileReader):
    def __init__(self):
        self.saver = False

    async def save(self, profile: Profile) -> None:
        self.saver = True

    async def by_identity(self, user_id: UserId) -> Profile | None:
        return Profile(profile_id=ProfileId(1), full_name="ABC", shop_id=None)

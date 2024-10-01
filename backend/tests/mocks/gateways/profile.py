from application.profile.gateway import ProfileSaver
from entities.profile.models import Profile


class FakeProfileGateway(ProfileSaver):
    def __init__(self):
        self.saver = False

    async def save(self, profile: Profile) -> None:
        self.saver = True

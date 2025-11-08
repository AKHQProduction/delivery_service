from backend.application.interfaces.idp import IdentityProvider
from backend.application.vars import UserId


class InMemoryIdentityProvider(IdentityProvider):
    def __init__(self, user_id: UserId | None = None) -> None:
        self.user_id = user_id

    async def current_user_id(self) -> UserId | None:
        return self.user_id

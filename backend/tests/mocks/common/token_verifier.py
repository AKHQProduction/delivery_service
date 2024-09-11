from entities.common.token_verifier import TokenVerifier
from entities.shop.value_objects import ShopToken


class FakeTokenVerifier(TokenVerifier):
    def __init__(self):
        self.verified = False

    async def verify_token(self, token: ShopToken) -> None:
        self.verified = True

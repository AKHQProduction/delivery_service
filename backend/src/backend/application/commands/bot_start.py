from dataclasses import dataclass

from backend.application.interfaces import (
    CreateUserViaTgDTO,
    ShopGateway,
    UserGateway,
)
from backend.application.interfaces.idp import IdentityProvider


@dataclass(frozen=True)
class BotStartCommand:
    tg_id: int
    full_name: str


class BotStartCommandHandler:
    def __init__(
        self,
        identity_provider: IdentityProvider,
        user_gateway: UserGateway,
        shop_gateway: ShopGateway,
    ) -> None:
        self._idp = identity_provider
        self._user_gateway = user_gateway
        self._shop_gateway = shop_gateway

    async def handle(self, command: BotStartCommand) -> bool:
        user_id = await self._idp.current_user_id()

        if not user_id:
            new_user_id = self._user_gateway.next_id()
            await self._user_gateway.create_user_via_tg(
                CreateUserViaTgDTO(
                    user_id=new_user_id,
                    tg_id=command.tg_id,
                    full_name=command.full_name,
                )
            )
            return False

        return await self._shop_gateway.relate_to_shop(user_id)

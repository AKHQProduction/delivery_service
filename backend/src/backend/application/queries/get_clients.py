from dataclasses import dataclass

from backend.application.interfaces import ClientGateway, IdentityProvider
from backend.application.interfaces.gateways import Pagination
from backend.application.interfaces.gateways.client_gateway import (
    ClientReadModel,
    GetClientsFilters,
)


@dataclass(frozen=True)
class GetClientsQuery:
    pagination: Pagination
    full_name: str | None = None
    custom_id: str | None = None
    phone: str | None = None


class GetClientsQueryHandler:
    def __init__(
        self, idp: IdentityProvider, client_gateway: ClientGateway
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway

    async def handle(self, query: GetClientsQuery) -> list[ClientReadModel]:
        current_user = await self._idp.current_user()

        return await self._client_gateway.read_all(
            filters=GetClientsFilters(
                shop_id=current_user.shop_id,
                full_name=query.full_name,
                custom_id=query.custom_id,
                phone=query.phone,
            ),
            pagination=query.pagination,
        )

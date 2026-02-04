from dataclasses import dataclass

from backend.application.dto.gateways import Pagination
from backend.application.dto.gateways.client_gateway import (
    ClientReadModel,
    GetClientsFilters,
)
from backend.infrastructure.idp import TelegramIdentityProvider
from backend.infrastructure.persistence.gateways import SQLAlchemyClientGateway


@dataclass(frozen=True)
class GetClientsQuery:
    pagination: Pagination
    full_name: str | None = None
    phone: str | None = None


class GetClientsQueryHandler:
    def __init__(
        self,
        idp: TelegramIdentityProvider,
        client_gateway: SQLAlchemyClientGateway,
    ) -> None:
        self._idp = idp
        self._client_gateway = client_gateway

    async def handle(self, query: GetClientsQuery) -> list[ClientReadModel]:
        current_user = await self._idp.current_user()

        return await self._client_gateway.read_all(
            filters=GetClientsFilters(
                shop_id=current_user.shop_id,
                full_name=query.full_name,
                phone=query.phone,
            ),
            pagination=query.pagination,
        )

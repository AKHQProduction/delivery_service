from dataclasses import dataclass
from typing import Sequence

from application.common.identity_provider import IdentityProvider
from application.common.persistence.employee import (
    EmployeeReader,
    EmployeeReaderFilters,
)
from application.common.persistence.shop import ShopGateway
from application.common.persistence.view_models import EmployeeView
from application.common.validators import validate_shop, validate_user


@dataclass
class GetEmployeeQueryHandler:
    identity_provider: IdentityProvider
    shop_gateway: ShopGateway
    employee_reader: EmployeeReader

    async def __call__(self) -> Sequence[EmployeeView]:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        filters = EmployeeReaderFilters(shop_id=shop.oid)

        return await self.employee_reader.read_many(filters)

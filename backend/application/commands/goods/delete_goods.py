import logging
from dataclasses import dataclass
from uuid import UUID

from application.common.access_service import AccessService
from application.common.file_manager import FileManager
from application.common.identity_provider import IdentityProvider
from application.common.persistence.goods import GoodsGateway
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import (
    validate_goods,
    validate_shop,
    validate_user,
)
from entities.goods.models import GoodsId
from entities.goods.service import GoodsService


@dataclass(frozen=True)
class DeleteGoodsCommand:
    goods_id: UUID


@dataclass
class DeleteGoodsCommandHandler:
    identity_provider: IdentityProvider
    access_service: AccessService
    shop_gateway: ShopGateway
    goods_gateway: GoodsGateway
    goods_service: GoodsService
    file_manager: FileManager
    transaction_manager: TransactionManager

    async def __call__(self, data: DeleteGoodsCommand) -> None:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        await self.access_service.ensure_can_delete_goods(actor.oid, shop.oid)

        goods_id = GoodsId(data.goods_id)

        goods = await self.goods_gateway.load_with_id(goods_id)
        validate_goods(goods, goods_id)

        if goods.metadata_path:
            self.file_manager.delete_object(goods.metadata_path)

        await self.goods_service.delete_goods(goods)

        await self.transaction_manager.commit()

        logging.info("Goods with id=%s was deleted", data.goods_id)

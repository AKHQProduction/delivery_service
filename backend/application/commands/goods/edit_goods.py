import logging
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from application.commands.goods.input_data import FileMetadata
from application.common.access_service import AccessService
from application.common.file_manager import FileManager, file_path_creator
from application.common.identity_provider import IdentityProvider
from application.common.persistence.goods import GoodsGateway
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import (
    validate_goods,
    validate_shop,
    validate_user,
)
from entities.common.vo import Price
from entities.goods.models import Goods, GoodsId, GoodsType
from entities.goods.service import GoodsService
from entities.goods.value_objects import GoodsTitle


@dataclass(frozen=True)
class EditGoodsInputData:
    goods_id: UUID
    title: str
    price: Decimal
    goods_type: GoodsType
    metadata: FileMetadata | None


@dataclass
class EditGoodsCommandHandler:
    identity_provider: IdentityProvider
    access_service: AccessService
    shop_gateway: ShopGateway
    goods_gateway: GoodsGateway
    goods_service: GoodsService
    file_manager: FileManager
    transaction_manager: TransactionManager

    async def __call__(self, data: EditGoodsInputData) -> None:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        await self.access_service.ensure_can_edit_goods(actor.oid, shop.oid)

        goods_id = GoodsId(data.goods_id)
        goods = await self.goods_gateway.load_with_id(goods_id)
        validate_goods(goods, goods_id)

        goods.title = GoodsTitle(data.title)
        goods.price = Price(data.price)
        goods.goods_type = data.goods_type
        self._process_file_metadata(goods, data.metadata)

        await self.transaction_manager.commit()

        logging.info("Edit goods with id=%s", goods_id)

    def _process_file_metadata(
        self, goods: Goods, metadata: FileMetadata | None
    ):
        if goods.metadata_path and not metadata:
            self.goods_service.set_path(goods, None)
            self.file_manager.delete_object(goods.metadata_path)
        if metadata:
            path = file_path_creator(goods.shop_id, goods.oid)
            self.goods_service.set_path(goods, None)
            self.file_manager.save(metadata.payload, path)

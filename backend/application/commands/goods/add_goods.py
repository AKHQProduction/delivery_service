import logging
from dataclasses import dataclass
from decimal import Decimal

from application.commands.goods.input_data import FileMetadata
from application.common.access_service import AccessService
from application.common.errors.goods import GoodsAlreadyExistsError
from application.common.file_manager import FileManager, file_path_creator
from application.common.identity_provider import IdentityProvider
from application.common.persistence.goods import GoodsGateway
from application.common.persistence.shop import ShopGateway
from application.common.transaction_manager import TransactionManager
from application.common.validators import validate_shop, validate_user
from entities.common.vo import Price
from entities.goods.models import Goods, GoodsId, GoodsType
from entities.goods.service import GoodsService
from entities.goods.value_objects import GoodsTitle
from entities.shop.models import ShopId


@dataclass(frozen=True)
class AddGoodsCommand:
    title: str
    price: Decimal
    goods_type: GoodsType
    metadata: FileMetadata | None = None


@dataclass
class AddGoodsCommandHandler:
    identity_provider: IdentityProvider
    access_service: AccessService
    shop_gateway: ShopGateway
    goods_gateway: GoodsGateway
    goods_service: GoodsService
    file_manager: FileManager
    transaction_manager: TransactionManager

    async def __call__(self, command: AddGoodsCommand) -> GoodsId:
        actor = await self.identity_provider.get_user()
        validate_user(actor)

        shop = await self.shop_gateway.load_with_identity(actor.oid)
        validate_shop(shop)

        await self.access_service.ensure_can_create_goods(actor.oid, shop.oid)

        if await self.goods_gateway.is_exist(command.title, shop.oid):
            raise GoodsAlreadyExistsError(command.title)

        title = GoodsTitle(command.title)
        price = Price(command.price)
        new_goods = self.goods_service.create_goods(
            shop.oid, title, price, command.goods_type
        )

        self._process_file_metadata(new_goods, shop.oid, command.metadata)

        await self.transaction_manager.commit()

        logging.info("Goods with id=%s successfully created", new_goods.oid)

        return new_goods.oid

    def _process_file_metadata(
        self, goods: Goods, shop_id: ShopId, metadata: FileMetadata | None
    ):
        if not metadata:
            return

        path = file_path_creator(shop_id, goods.oid)

        self.file_manager.save(payload=metadata.payload, path=path)
        self.goods_service.set_path(goods, path)

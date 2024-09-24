import logging
import uuid
from dataclasses import dataclass
from decimal import Decimal

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.file_manager import FileManager
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.goods.gateway import GoodsSaver
from application.goods.input_data import FileMetadata
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopReader
from application.user.errors import UserIsNotExistError
from entities.goods.models import Goods, GoodsId
from entities.goods.value_objects import GoodsPrice, GoodsTitle
from entities.shop.models import ShopId


@dataclass(frozen=True)
class AddGoodsInputData:
    title: str
    price: Decimal
    metadata: FileMetadata | None = None


class AddGoods(Interactor[AddGoodsInputData, GoodsId]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        access_service: AccessService,
        shop_reader: ShopReader,
        goods_saver: GoodsSaver,
        file_manager: FileManager,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._access_service = access_service
        self._shop_reader = shop_reader
        self._goods_saver = goods_saver
        self._file_manager = file_manager
        self._commiter = commiter

    async def __call__(self, data: AddGoodsInputData) -> GoodsId:
        actor = await self._identity_provider.get_user()
        if not actor:
            raise UserIsNotExistError()

        shop = await self._shop_reader.by_identity(actor.user_id)
        if not shop:
            raise UserNotHaveShopError(actor.user_id)

        await self._access_service.ensure_can_create_goods(
            actor.user_id, shop.shop_id
        )

        goods_id = GoodsId(uuid.uuid4())
        path = self._process_file_metadata(
            goods_id, shop.shop_id, data.metadata
        )

        new_goods = Goods(
            goods_id=goods_id,
            shop_id=shop.shop_id,
            title=GoodsTitle(data.title),
            price=GoodsPrice(data.price),
            metadata_path=path,
        )

        await self._goods_saver.save(new_goods)

        await self._commiter.commit()

        logging.info("Goods with id=%s successfully created", goods_id)

        return new_goods.goods_id

    def _process_file_metadata(
        self, goods_id: GoodsId, shop_id: ShopId, metadata: FileMetadata | None
    ) -> str | None:
        if not metadata:
            return None

        path = f"{shop_id}/{goods_id}.{metadata.extension}"

        self._file_manager.save(payload=metadata.payload, path=path)

        return path

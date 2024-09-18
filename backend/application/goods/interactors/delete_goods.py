import logging
from dataclasses import dataclass
from uuid import UUID

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.file_manager import FileManager
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.goods.errors import GoodsIsNotExistError
from application.goods.gateway import GoodsReader, GoodsSaver
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopReader
from application.user.errors import UserIsNotExistError
from entities.goods.models import GoodsId


@dataclass(frozen=True)
class DeleteGoodsInputData:
    goods_id: UUID


class DeleteGoods(Interactor[DeleteGoodsInputData, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        access_service: AccessService,
        shop_reader: ShopReader,
        goods_saver: GoodsSaver,
        goods_reader: GoodsReader,
        file_manager: FileManager,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._access_service = access_service
        self._shop_reader = shop_reader
        self._goods_saver = goods_saver
        self._goods_reader = goods_reader
        self._file_manager = file_manager
        self._commiter = commiter

    async def __call__(self, data: DeleteGoodsInputData) -> None:
        actor = await self._identity_provider.get_user()
        if not actor:
            raise UserIsNotExistError()

        shop = await self._shop_reader.by_identity(actor.user_id)
        if not shop:
            raise UserNotHaveShopError(actor.user_id)

        await self._access_service.ensure_can_delete_goods(
            actor.user_id, shop.shop_id
        )

        goods_id = GoodsId(data.goods_id)

        goods = await self._goods_reader.by_id(goods_id)
        if not goods:
            GoodsIsNotExistError(goods_id)

        if goods.metadata_path:
            self._file_manager.delete(goods.metadata_path)

        await self._goods_saver.delete(goods)

        await self._commiter.commit()

        logging.info("Goods with id=%s was deleted", data.goods_id)

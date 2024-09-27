import logging
from dataclasses import dataclass
from uuid import UUID

from application.common.access_service import AccessService
from application.common.commiter import Commiter
from application.common.file_manager import FileManager, file_path_creator
from application.common.identity_provider import IdentityProvider
from application.common.interactor import Interactor
from application.goods.errors import GoodsIsNotExistError
from application.goods.gateway import GoodsReader
from application.goods.input_data import FileMetadata
from application.shop.errors import UserNotHaveShopError
from application.shop.gateway import ShopReader
from application.user.errors import UserIsNotExistError
from entities.goods.models import Goods, GoodsId


@dataclass(frozen=True)
class EditGoodsPicInputData:
    goods_id: UUID
    metadata: FileMetadata | None = None


class EditGoodsPic(Interactor[EditGoodsPicInputData, None]):
    def __init__(
        self,
        identity_provider: IdentityProvider,
        access_service: AccessService,
        shop_reader: ShopReader,
        goods_reader: GoodsReader,
        file_manager: FileManager,
        commiter: Commiter,
    ):
        self._identity_provider = identity_provider
        self._shop_reader = shop_reader
        self._access_service = access_service
        self._goods_reader = goods_reader
        self._file_manager = file_manager
        self._commiter = commiter

    async def __call__(self, data: EditGoodsPicInputData) -> None:
        actor = await self._identity_provider.get_user()
        if not actor:
            raise UserIsNotExistError()

        shop = await self._shop_reader.by_identity(actor.user_id)
        if not shop:
            raise UserNotHaveShopError(actor.user_id)

        await self._access_service.ensure_can_edit_goods(
            actor.user_id, shop.shop_id
        )

        goods_id = GoodsId(data.goods_id)

        goods = await self._goods_reader.by_id(goods_id)
        if not goods:
            raise GoodsIsNotExistError(goods_id)

        goods.metadata_path = self._process_file_metadata(goods, data.metadata)

        await self._commiter.commit()

        logging.info("Edit goods pic with id=%s", goods_id)

    def _process_file_metadata(
        self, goods: Goods, metadata: FileMetadata | None
    ) -> str | None:
        if not goods.metadata_path and not metadata:
            return None

        if goods.metadata_path and not metadata:
            return self._file_manager.delete_object(goods.metadata_path)

        path = file_path_creator(goods.shop_id, goods.goods_id)

        self._file_manager.save(metadata.payload, path)

        return path

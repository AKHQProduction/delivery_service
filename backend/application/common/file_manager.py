from abc import abstractmethod
from asyncio import Protocol

from entities.goods.models import GoodsId
from entities.shop.models import ShopId


def file_path_creator(
    shop_id: ShopId, goods_id: GoodsId, extension: str = "jpg"
) -> str:
    return f"{shop_id}/{goods_id}.{extension}"


class FileManager(Protocol):
    @abstractmethod
    def save(self, payload: bytes, path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_file_id(self, file_path: str) -> bytes | None:
        raise NotImplementedError

    @abstractmethod
    def delete_object(self, path: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_folder(self, folder: str) -> None:
        raise NotImplementedError

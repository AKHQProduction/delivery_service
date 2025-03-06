from typing import Any

from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.persistence.goods import GoodsReader
from presentation.common.consts import ACTUAL_GOODS_TYPES


async def get_goods_types(**_kwargs) -> dict[str, Any]:
    return {"types": list(ACTUAL_GOODS_TYPES.items())}


@inject
async def goods_view_getter(
    goods_reader: FromDishka[GoodsReader],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    goods_id = dialog_manager.dialog_data["goods_id"]

    goods = await goods_reader.read_with_id(goods_id)
    if not goods:
        pass

    title = str(goods.title)
    price = str(goods.price)
    category_type = goods.goods_type
    category = ACTUAL_GOODS_TYPES[category_type]
    path = goods.metadata_path

    dialog_manager.dialog_data["goods_id"] = goods_id
    dialog_manager.dialog_data["title"] = title
    dialog_manager.dialog_data["price"] = price
    dialog_manager.dialog_data["category_type"] = category_type
    dialog_manager.dialog_data["category"] = category
    dialog_manager.dialog_data["path"] = path

    return dialog_manager.dialog_data


goods_card_photo = DynamicMedia(selector="media", when=F["media"])
goods_card_txt = Multi(
    Format("🏷 <b>Назва:</b> {dialog_data[title]}"),
    Format("💸 <b>Ціна:</b> {dialog_data[price]} UAH"),
    Format("📜 <b>Категорія:</b> {dialog_data[category]}"),
)


async def photo_getter(
    dialog_manager: DialogManager, **_kwargs
) -> dict[str, Any] | None:
    media = None

    if path := dialog_manager.dialog_data.get("path"):
        media = MediaAttachment(type=ContentType.PHOTO, url=path)

    if file_id := dialog_manager.dialog_data.get("file_id"):
        media = MediaAttachment(
            type=ContentType.PHOTO, file_id=MediaId(file_id)
        )

    return {"media": media}

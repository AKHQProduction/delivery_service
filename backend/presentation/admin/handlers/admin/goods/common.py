from typing import Any

from aiogram import F
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Multi

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

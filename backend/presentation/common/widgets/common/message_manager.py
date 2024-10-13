from typing import Union

from aiogram import Bot
from aiogram.types import BufferedInputFile, InputFile, URLInputFile
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.manager.message_manager import MessageManager
from dishka import AsyncContainer

from application.common.file_manager import FileManager


class CustomMessageManager(MessageManager):
    def __init__(self, container: AsyncContainer):
        self.container = container

    async def get_media_source(
        self, media: MediaAttachment, bot: Bot
    ) -> Union[InputFile, str]:
        if media.file_id:
            return await super().get_media_source(media, bot)
        if media.url:
            return await self._fetch_media_from_s3(media.url)
        return await super().get_media_source(media, bot)

    async def _fetch_media_from_s3(self, file_path: str) -> InputFile:
        s3: FileManager = await self.container.get(FileManager)
        not_found_photo_url = (
            "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/"
            "No-Image-Placeholder.svg/660px-No-Image-"
            "Placeholder.svg.png?20200912122019"
        )

        try:
            file = s3.get_by_file_id(file_path)
        except Exception:  # noqa: ignore
            return URLInputFile(not_found_photo_url)
        else:
            return (
                BufferedInputFile(file, file_path)
                if file
                else URLInputFile(not_found_photo_url)
            )

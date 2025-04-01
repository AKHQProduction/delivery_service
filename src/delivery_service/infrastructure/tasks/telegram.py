# ruff: noqa: E501
from dishka import FromDishka
from dishka.integrations.taskiq import inject

from delivery_service.infrastructure.integration.telegram.check_telegram_users import (
    CheckTelegramUsers,
)


@inject
async def check_for_update_telegram_users(
    task: FromDishka[CheckTelegramUsers],
) -> None:
    await task.handle()

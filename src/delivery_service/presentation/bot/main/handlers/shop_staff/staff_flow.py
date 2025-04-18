from typing import Any
from uuid import UUID

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.utils.deep_linking import create_start_link
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.api.internal import Widget
from aiogram_dialog.widgets.kbd import Button, ScrollingGroup, Select, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Jinja
from bazario.asyncio import Sender
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from delivery_service.application.commands.discard_staff_member import (
    DiscardStaffMemberRequest,
)
from delivery_service.application.query.ports.staff_gateway import (
    StaffMemberGateway,
)
from delivery_service.application.query.shop import (
    GetShopRequest,
    GetShopStaffMembersRequest,
)
from delivery_service.domain.shared.errors import AccessDeniedError
from delivery_service.domain.shared.user_id import UserID
from delivery_service.domain.shops.errors import CantDiscardYourselfError
from delivery_service.domain.staff.staff_role import Role
from delivery_service.infrastructure.integration.telegram.const import (
    STAFF_BTN,
)
from delivery_service.presentation.bot.widgets.kbd import get_back_btn

from .states import StaffMenu

STAFF_ROUTER = Router()


@STAFF_ROUTER.message(F.text == STAFF_BTN)
async def launch_staff_dialogs(
    _: Message, dialog_manager: DialogManager
) -> None:
    await dialog_manager.start(
        state=StaffMenu.MAIN, mode=StartMode.RESET_STACK
    )


@inject
async def get_invite_manager_link(
    dialog_manager: DialogManager, sender: FromDishka[Sender], **_kwargs
) -> dict[str, Any]:
    bot: Bot | None = dialog_manager.middleware_data.get("bot")
    if not bot:
        raise ValueError()

    shop = await sender.send(GetShopRequest())
    link = await create_start_link(bot, payload=f"add_staff_{shop.shop_id}")

    return {"link": link}


@inject
async def get_shop_staff_members(
    sender: FromDishka[Sender], **_kwargs
) -> dict[str, Any]:
    response = await sender.send(GetShopStaffMembersRequest())

    return {"members": response.staff, "total": response.total}


ROLE_TO_TEXT = {
    Role.SHOP_OWNER: "🫅 Адмінінстратор",
    Role.SHOP_MANAGER: "👩‍💻 Менеджер",
    Role.COURIER: "🚚 Кур'єр",
}


@inject
async def get_shop_staff_member(
    staff_reader: FromDishka[StaffMemberGateway],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    if staff_id := dialog_manager.dialog_data.get("staff_id"):
        member = await staff_reader.read_staff_member(staff_id)
        if not member:
            raise ValueError()

        dialog_manager.dialog_data["full_name"] = member.full_name
        roles = [ROLE_TO_TEXT[role] for role in member.roles]
        return {"full_name": member.full_name, "roles": roles}
    raise ValueError()


async def on_select_staff_member_item(
    _: CallbackQuery, __: Widget, manager: DialogManager, value: str
) -> None:
    manager.dialog_data["staff_id"] = value
    await manager.switch_to(state=StaffMenu.STAFF_CARD)


@inject
async def on_accept_staff_delete(
    call: CallbackQuery,
    __: Button,
    manager: DialogManager,
    sender: FromDishka[Sender],
) -> None:
    if not call.message:
        raise ValueError()

    if staff_id := manager.dialog_data.get("staff_id"):
        try:
            await sender.send(
                DiscardStaffMemberRequest(
                    staff_member_id=UserID(UUID(staff_id))
                )
            )
            await call.message.answer("✅ Успішно видалено")
        except AccessDeniedError:
            await call.message.answer("❌ Дія заборонена")
        except CantDiscardYourselfError:
            await call.message.answer("❌ Неможна видалити себе")

        return await manager.switch_to(
            state=StaffMenu.MAIN, show_mode=ShowMode.SEND
        )
    raise ValueError()


STAFF_DIALOG = Dialog(
    Window(
        Const("<b>Меню персоналу</b>\n"),
        Format("<b>Посилання для менеджера:</b> <code>{link}</code>\n"),
        Const(
            "<i>Відправте посилання вашому менеджеру."
            " Після вступу в бот він автоматично потрапить до вашої команди"
            "</i>"
        ),
        ScrollingGroup(
            Select(
                id="s_staff_member",
                items="members",
                item_id_getter=lambda item: item.staff_id,
                text=Format("{pos}. {item.full_name}"),
                on_click=on_select_staff_member_item,
            ),
            id="all_shop_staff_members",
            width=2,
            height=10,
            hide_on_single_page=True,
            when=F["total"] > 0,
        ),
        getter=[get_invite_manager_link, get_shop_staff_members],
        state=StaffMenu.MAIN,
    ),
    Window(
        Format("<b>Ім'я:</b> {full_name}"),
        Jinja(
            "<b>Права:</b>\n"
            "{% for role in roles %}"
            "- {{ role }}\n"
            "{% endfor %}"
        ),
        SwitchTo(
            id="delete_staff_member",
            text=Const("🗑 Видалить"),
            state=StaffMenu.DELETE_CONFIRMATION,
        ),
        get_back_btn(),
        getter=get_shop_staff_member,
        state=StaffMenu.STAFF_CARD,
    ),
    Window(
        Format("Підтвердіть видалення {dialog_data[full_name]}"),
        Button(
            text=Const("✅ Підтвердити"),
            id="accept_staff_delete",
            on_click=on_accept_staff_delete,
        ),
        get_back_btn(btn_text="❌ Відмінити", state=StaffMenu.STAFF_CARD),
        state=StaffMenu.DELETE_CONFIRMATION,
    ),
)

import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Group, Select
from aiogram_dialog.widgets.text import Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.persistence.employee import EmployeeReader
from application.queries.employee.get_employees import (
    GetEmployeeQueryHandler,
)
from entities.employee.models import EmployeeRole
from presentation.common.consts import ACTUAL_ROLES


async def get_actual_employee_roles(**_kwargs) -> dict[str, Any]:
    return {
        "roles": [
            (key, value)
            for key, value in ACTUAL_ROLES.items()
            if key != EmployeeRole.ADMIN
        ]
    }


async def on_role_selected(
    _: CallbackQuery, __: Select, manager: DialogManager, value: EmployeeRole
) -> None:
    manager.dialog_data["role"] = value

    await manager.next()


select_employee_role_widget = Group(
    Select(
        text=Format("{item[1]}"),
        id="select_employee_role",
        items="roles",
        item_id_getter=operator.itemgetter(0),
        type_factory=lambda x: EmployeeRole(x),
        on_click=on_role_selected,  # type: ignore[arg-type]
    ),
    width=2,
)


@inject
async def get_employee_cards(
    action: FromDishka[GetEmployeeQueryHandler],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    output_data = await action()

    dialog_manager.dialog_data["total"] = len(output_data)
    dialog_manager.dialog_data["employee_cards"] = [
        (
            card.employee_id,
            card.user_id,
            card.full_name,
            ACTUAL_ROLES[card.role],
        )
        for card in output_data
    ]

    return dialog_manager.dialog_data


employee_card = Multi(
    Format("<b>Ім'я</b>: {dialog_data[full_name]}"),
    Format("<b>Посада</b>: {dialog_data[role_txt]}"),
)


@inject
async def get_employee_card(
    employee_reader: FromDishka[EmployeeReader],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    employee_id = int(dialog_manager.dialog_data["employee_id"])

    employee = await employee_reader.read_with_id(employee_id)
    if not employee:
        return None

    dialog_manager.dialog_data["employee_id"] = employee_id
    dialog_manager.dialog_data["full_name"] = employee.full_name
    dialog_manager.dialog_data["role"] = employee.role
    dialog_manager.dialog_data["role_txt"] = ACTUAL_ROLES[employee.role]

    return dialog_manager.dialog_data

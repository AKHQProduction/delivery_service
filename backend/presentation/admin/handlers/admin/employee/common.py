import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Group, Select
from aiogram_dialog.widgets.text import Format, Multi
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.input_data import Pagination
from application.employee.gateway import EmployeeFilters
from application.employee.queries.get_employee_card import (
    GetEmployeeCard,
    GetEmployeeCardInputData,
)
from application.employee.queries.get_employees_cards import (
    GetEmployeeCards,
    GetEmployeeCardsInputData,
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
    action: FromDishka[GetEmployeeCards],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    output_data = await action(
        GetEmployeeCardsInputData(
            filters=EmployeeFilters(), pagination=Pagination()
        )
    )

    dialog_manager.dialog_data["total"] = output_data.total
    dialog_manager.dialog_data["employee_cards"] = [
        (
            card.employee_id,
            card.user_id,
            card.full_name,
            ACTUAL_ROLES[card.role],
        )
        for card in output_data.employees_card
    ]

    return dialog_manager.dialog_data


employee_card = Multi(
    Format("<b>Ім'я</b>: {dialog_data[full_name]}"),
    Format("<b>Посада</b>: {dialog_data[role_txt]}"),
)


@inject
async def get_employee_card(
    action: FromDishka[GetEmployeeCard],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    employee_id = int(dialog_manager.dialog_data["employee_id"])

    output_data = await action(GetEmployeeCardInputData(employee_id))

    dialog_manager.dialog_data["employee_id"] = employee_id
    dialog_manager.dialog_data["full_name"] = output_data.full_name
    dialog_manager.dialog_data["role"] = output_data.role
    dialog_manager.dialog_data["role_txt"] = ACTUAL_ROLES[output_data.role]

    return dialog_manager.dialog_data

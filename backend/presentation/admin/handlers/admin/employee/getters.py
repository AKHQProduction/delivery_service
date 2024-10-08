from typing import Any

from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from application.common.input_data import Pagination
from application.employee.gateway import EmployeeFilters
from application.employee.query.get_employees_cards import (
    GetEmployeeCardInputData,
    GetEmployeeCards,
)
from presentation.common.consts import ACTUAL_ROLES


@inject
async def get_employee_cards(
    action: FromDishka[GetEmployeeCards],
    dialog_manager: DialogManager,
    **_kwargs,
) -> dict[str, Any]:
    output_data = await action(
        GetEmployeeCardInputData(
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

import operator
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Group, Select
from aiogram_dialog.widgets.text import Format

from entities.employee.models import EmployeeRole
from presentation.common.consts import ACTUAL_ROLES


async def get_actual_employee_roles(**_kwargs) -> dict[str, Any]:
    return {"roles": [(value, key) for key, value in ACTUAL_ROLES.items()]}


async def on_role_selected(
    _: CallbackQuery, __: Select, manager: DialogManager, value: EmployeeRole
) -> None:
    manager.dialog_data["role"] = value

    await manager.next()


select_employee_role_widget = Group(
    Select(
        text=Format("{item[0]}"),
        id="select_employee_role",
        items="roles",
        item_id_getter=operator.itemgetter(1),
        type_factory=lambda x: EmployeeRole(x),
        on_click=on_role_selected,  # type: ignore[arg-type]
    ),
    width=2,
)

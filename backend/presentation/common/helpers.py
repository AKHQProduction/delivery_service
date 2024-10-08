from aiogram.fsm.state import State
from aiogram_dialog import DialogManager


async def step_toggler_in_form(
    manager: DialogManager, key: str, state: State
) -> None:
    flag = manager.dialog_data.get(key, False)

    await manager.switch_to(state=state) if flag else await manager.next()

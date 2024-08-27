from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog.widgets.kbd import Next


class ChangeUserRole(StatesGroup):
    ID = State()
    SELECT_USER_ROLE = State()
    CONFIRMATION = State()

from aiogram.fsm.state import State, StatesGroup
from aiogram_dialog.widgets.kbd import Next


class AddToStaff(StatesGroup):
    ID = State()
    SELECT_USER_ROLE = State()
    CONFIRMATION = State()

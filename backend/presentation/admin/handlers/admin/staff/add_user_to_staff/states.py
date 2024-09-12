from aiogram.fsm.state import State, StatesGroup


class ChangeUserRole(StatesGroup):
    ID = State()
    SELECT_USER_ROLE = State()
    CONFIRMATION = State()

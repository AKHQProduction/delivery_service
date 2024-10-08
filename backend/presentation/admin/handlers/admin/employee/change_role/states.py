from aiogram.fsm.state import State, StatesGroup


class ChangeRole(StatesGroup):
    SELECT_EMPLOYEE_ROLE = State()
    CONFIRMATION = State()

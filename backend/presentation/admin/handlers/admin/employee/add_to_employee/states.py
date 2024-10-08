from aiogram.fsm.state import State, StatesGroup


class AddToEmployee(StatesGroup):
    FIND = State()
    SELECT_EMPLOYEE_ROLE = State()
    CONFIRMATION = State()

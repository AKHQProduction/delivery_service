from aiogram.fsm.state import State, StatesGroup


class EmployeeWorkflow(StatesGroup):
    MAIN_MENU = State()

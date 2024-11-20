from aiogram.fsm.state import State, StatesGroup


class EmployeeWorkflow(StatesGroup):
    MAIN_MENU = State()


class AddToEmployee(StatesGroup):
    FIND = State()
    SELECT_EMPLOYEE_ROLE = State()
    CONFIRMATION = State()


class ViewEmployee(StatesGroup):
    VIEW = State()
    DELETE = State()


class EditEmployee(StatesGroup):
    MAIN = State()
    ROLE = State()

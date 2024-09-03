from aiogram.fsm.state import State, StatesGroup


class DeleteUserFromStaff(StatesGroup):
    CONFIRMATION = State()

from aiogram.fsm.state import State, StatesGroup


class RemoveFromEmployee(StatesGroup):
    CONFIRMATION = State()

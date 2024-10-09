from aiogram.fsm.state import State, StatesGroup


class ProfileMainMenu(StatesGroup):
    MAIN = State()


class ProfileChangePhone(StatesGroup):
    NEW_PHONE = State()
    CONFIRMATION = State()

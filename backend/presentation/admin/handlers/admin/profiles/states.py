from aiogram.fsm.state import State, StatesGroup


class ProfileMenu(StatesGroup):
    VIEW = State()


class AddProfile(StatesGroup):
    NAME = State()

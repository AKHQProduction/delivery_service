from aiogram.fsm.state import State, StatesGroup


class ShopCreation(StatesGroup):
    SHOP_NAME = State()
    SHOP_DAYS_OFF = State()
    SHOP_LOCATION = State()
    PREVIEW = State()

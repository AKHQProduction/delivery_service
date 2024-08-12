from aiogram.fsm.state import StatesGroup, State


class CreateOrder(StatesGroup):
    WATER_TYPE = State()
    QUANTITY = State()
    DELIVERY_DATE = State()
    DELIVERY_TIME = State()
    ADDRESS = State()
    PHONE = State()
    CONFIRMATION = State()

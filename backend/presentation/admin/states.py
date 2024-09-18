from aiogram.fsm.state import State, StatesGroup


class CreateOrder(StatesGroup):
    WATER_TYPE = State()
    QUANTITY = State()
    DELIVERY_DATE = State()
    DELIVERY_TIME = State()
    ADDRESS = State()
    APARTMENT = State()
    PHONE = State()
    CONFIRMATION = State()

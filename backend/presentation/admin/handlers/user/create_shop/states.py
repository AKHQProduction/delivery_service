from aiogram.fsm.state import State, StatesGroup


class CreateShopStates(StatesGroup):
    TITLE = State()
    TOKEN = State()
    DAYS_OFF = State()
    DELIVERY_DISTANCE = State()
    LOCATION = State()
    REVIEW = State()
    FINISH = State()

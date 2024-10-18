from aiogram.fsm.state import State, StatesGroup


class Cart(StatesGroup):
    CART = State()
    EDIT_CART = State()
    GOODS_CATEGORY = State()
    GOODS_LIST = State()
    GOODS_VIEW = State()


class CreateOrder(StatesGroup):
    DATE = State()
    TIME = State()
    BOTTLE_QUANTITY = State()
    ADDRESS = State()
    PHONE = State()
    CONFIRMATION = State()

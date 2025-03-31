from aiogram.fsm.state import State, StatesGroup


class GoodsWorkflow(StatesGroup):
    MAIN_MENU = State()


class AddNewGoods(StatesGroup):
    TITLE = State()
    PRICE = State()
    GOODS_TYPE = State()
    METADATA = State()
    PREVIEW = State()


class ViewGoods(StatesGroup):
    VIEW = State()
    DELETE = State()


class EditGoods(StatesGroup):
    START = State()
    TITLE = State()
    PRICE = State()
    GOODS_TYPE = State()
    METADATA = State()
    PREVIEW = State()

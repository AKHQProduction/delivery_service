from aiogram.fsm.state import State, StatesGroup


class ProductMenu(StatesGroup):
    MAIN = State()

    PRODUCT_CARD = State()

    # Product creation
    PRODUCT_TITLE = State()
    PRODUCT_PRICE = State()
    PRODUCT_TYPE = State()
    PREVIEW = State()

    # Product editing
    EDIT_MENU = State()
    EDIT_PRODUCT_TITLE = State()
    EDIT_PRODUCT_PRICE = State()

    DELETE_CONFIRMATION = State()

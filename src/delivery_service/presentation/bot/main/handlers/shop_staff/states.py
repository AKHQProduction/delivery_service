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


class StaffMenu(StatesGroup):
    MAIN = State()
    STAFF_CARD = State()
    DELETE_CONFIRMATION = State()


class CustomerMenu(StatesGroup):
    MAIN = State()

    CUSTOMER_CARD = State()

    # Customer creation
    NEW_CUSTOMER_NAME = State()
    NEW_CUSTOMER_PHONE = State()
    NEW_CUSTOMER_ADDRESS = State()
    NEW_CUSTOMER_FLOOR = State()
    NEW_CUSTOMER_APARTMENT_NUMBER = State()
    NEW_CUSTOMER_INTERCOM_CODE = State()
    PREVIEW = State()

    EDIT_MENU = State()
    EDIT_CUSTOMER_NAME = State()
    EDIT_CUSTOMER_PHONE = State()
    EDIT_CUSTOMER_ADDRESS = State()
    EDIT_CUSTOMER_FLOOR = State()
    EDIT_CUSTOMER_APARTMENT_NUMBER = State()
    EDIT_CUSTOMER_INTERCOM_CODE = State()

    DELETE_CONFIRMATION = State()

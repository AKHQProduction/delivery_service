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

    ADDRESSES_MENU = State()
    ADDRESS_CARD = State()
    DELETE_ADDRESS = State()

    PHONE_NUMBERS_MENU = State()
    PHONE_NUMBER_CARD = State()
    DELETE_PHONE_NUMBER = State()
    ADD_PHONE_NUMBER = State()

    # Customer creation
    NEW_CUSTOMER_NAME = State()
    NEW_CUSTOMER_PHONE = State()
    NEW_CUSTOMER_ADDRESS = State()
    NEW_CUSTOMER_FLOOR = State()
    NEW_CUSTOMER_APARTMENT_NUMBER = State()
    NEW_CUSTOMER_INTERCOM_CODE = State()
    PREVIEW = State()

    # Customer editing
    EDIT_MENU = State()
    EDIT_CUSTOMER_NAME = State()

    DELETE_CONFIRMATION = State()


class OrderMenu(StatesGroup):
    MAIN = State()

    ORDER_CARD = State()
    ORDER_DELETE_CONFIRMATION = State()

    # Order creation
    FIND_CUSTOMER = State()
    SELECT_ADDRESS = State()
    CART = State()
    PRODUCTS_CATEGORY = State()
    PRODUCTS_CATALOG = State()
    PRODUCT_COUNTER = State()
    SELECT_DATE = State()
    SELECT_DELIVERY_PREFERENCE = State()
    NOTE = State()
    PREVIEW = State()

    # Editing
    EDITING_MENU = State()
    ITEM_EDITING_MENU = State()
    EDIT_QUANTITY = State()

    # Order reports
    SELECT_DATE_FOR_REPORT = State()


class AddressSG(StatesGroup):
    FULL_ADDRESS = State()
    FLOOR = State()
    APARTMENT_NUMBER = State()
    INTERCOM_CODE = State()

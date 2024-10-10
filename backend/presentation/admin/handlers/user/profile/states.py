from aiogram.fsm.state import State, StatesGroup


class ProfileMainMenu(StatesGroup):
    MAIN = State()


class ProfileChangePhone(StatesGroup):
    NEW_PHONE = State()
    CONFIRMATION = State()


class ProfileChangeAddress(StatesGroup):
    NEW_ADDRESS = State()


class AddressInputByTg(StatesGroup):
    SEND_LOCATION = State()
    CONFIRMATION = State()


class OtherInformationAboutAddress(StatesGroup):
    APARTMENT_NUMBER = State()
    FLOOR = State()
    INTERCOM_CODE = State()
    CONFIRMATION = State()

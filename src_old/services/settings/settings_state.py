from telebot.handler_backends import State, StatesGroup

class SettingsState(StatesGroup):
    waiting_sheet = State()
    waiting_link = State()
    waiting_default = State()
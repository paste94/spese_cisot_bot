from telebot.handler_backends import State, StatesGroup

class MessageState(StatesGroup):
    waiting_split_decision = State()
# class _SettingsState: 
#     state = {} # None, select_sheet, new_sheet, is_default
#     link = {}

#     def set_select_sheet(self, chat_id):
#         self.state[chat_id] = 'select_sheet'

#     def set_new_sheet(self, chat_id):
#         self.state[chat_id] = 'new_sheet'

#     def set_is_default(self, chat_id):
#         self.state[chat_id] = 'is_default'

#     def set_link(self, chat_id, link):
#         self.link[chat_id] = link

#     def get_state(self, chat_id):
#         if chat_id in self.state:
#             return self.state[chat_id]
#         return None

#     def get_link(self, chat_id):
#         if chat_id in self.link:
#             return self.link[chat_id]
#         return None
    
#     def reset_state(self, chat_id):
#         self.state[chat_id] = None
#         self.link[chat_id] = None

# SETTINGS_STATE = _SettingsState()

from telebot.handler_backends import State, StatesGroup

class SettingsState(StatesGroup):
    waiting_sheet = State()
    waiting_link = State()
    waiting_default = State()
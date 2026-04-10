import threading
from services.messages.message_state import MessageState
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TIMEOUT_SECONDS
from bot_instance import bot
from services.gsheet.utils import add_row
from services.utilities import handle_errors, parse_message
from services.users.users import USERS

@bot.message_handler(func=lambda msg: True)
@handle_errors(bot)
def get_message(message):
    if not USERS.is_authorized(message.from_user.username):
        bot.reply_to(message, "❌ Non sei autorizzato a inviare messaggi.")
        return

    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    row = parse_message(message.text)
    if row['split'] == False:
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("✅ Sì", callback_data="si"),
            InlineKeyboardButton("❌ No (Default)", callback_data="no")
        )

        bot.set_state(user_id , MessageState.waiting_split_decision, chat_id)
        bot.send_message(chat_id, f"🤔 Vuoi che questa spesa sia divisa? ({TIMEOUT_SECONDS}s timeout)", reply_markup=markup)
        with bot.retrieve_data(user_id, chat_id) as data:
            data["timer"] = timer
            data["row"] = row

        timer = threading.Timer(
            TIMEOUT_SECONDS,
            on_timeout,
            args=[chat_id, user_id, username]
        )
        timer.start()
    else:
        handle_add_row(row, username, chat_id, user_id)

@bot.message_handler(state=MessageState.waiting_split_decision)
@handle_errors(bot)
def get_message(message):
    if not USERS.is_authorized(message.from_user.username):
        bot.reply_to(message, "❌ Non sei autorizzato a inviare messaggi.")
        return
    
    chat_id = message.chat.id
    user_id = message.from_user.id
    username = message.from_user.username

    with bot.retrieve_data(user_id, chat_id) as data:
        row = data["row"]
        data['row'] = None

    if message.data == "si":
        row['split'] = True 
    handle_add_row(row, username, chat_id, user_id)

def on_timeout(chat_id: str, user_id: str, username: str):
    with bot.retrieve_data(user_id, chat_id) as data:
        row = data["row"]
    handle_add_row(row, username, chat_id, user_id)

def handle_add_row(row, username, chat_id, user_id):
    add_row(row, username)
    bot.delete_state(user_id, chat_id)
    bot.send_message(chat_id, f"✅ Spesa aggiunta: {row['description']} - {row['price']}€ {'(diviso)' if row['split'] else ''}")
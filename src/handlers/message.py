import logging
import threading
from services.messages.message_state import MessageState
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TIMEOUT_SECONDS
from bot_instance import bot
from services.gsheet.utils import add_row
from services.utilities import handle_errors, parse_message
from services.users.users import USERS

logger = logging.getLogger(__name__)

active_timers: dict = {}

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
            InlineKeyboardButton("✅ Sì", callback_data="si_split"),
            InlineKeyboardButton("❌ No (Default)", callback_data="no_split")
        )
        
        sent = bot.send_message(chat_id, f"🤔 Vuoi che questa spesa sia divisa? ({TIMEOUT_SECONDS}s timeout)", reply_markup=markup)
        bot.set_state(user_id , MessageState.waiting_split_decision, chat_id)
        with bot.retrieve_data(user_id, chat_id) as data:
            # data["timer"] = timer
            data["row"] = row

        start_timeout(chat_id, user_id, username, TIMEOUT_SECONDS, sent.message_id)
    else:
        handle_add_row(row, username, chat_id, user_id)

@bot.callback_query_handler(func=lambda call: call.data in ["si_split", "no_split"])
@handle_errors(bot)
def handle_split_response(call):
    user_id = call.from_user.id
    with bot.retrieve_data(user_id, call.message.chat.id) as data:
        row = data.get("row")

    if call.data == "si_split":
        row["split"] = True
    
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🤔 Vuoi che questa spesa sia divisa? → {'✅ Sì' if call.data == 'si_split' else '❌ No'}",
        reply_markup=None  # rimuove i bottoni
    )
    bot.answer_callback_query(call.id)

    bot.send_message(call.message.chat.id, f"Ok, attendi che la spesa venga caricata...")
    handle_add_row(row, call.from_user.username, call.message.chat.id, user_id)
    # bot.delete_state(user_id, call.message.chat.id)

# @bot.message_handler(state=MessageState.waiting_split_decision)
# @handle_errors(bot)
# def get_message(message):
#     if not USERS.is_authorized(message.from_user.username):
#         bot.reply_to(message, "❌ Non sei autorizzato a inviare messaggi.")
#         return
    
#     chat_id = message.chat.id
#     user_id = message.from_user.id
#     username = message.from_user.username

#     with bot.retrieve_data(user_id, chat_id) as data:
#         row = data["row"]
#         data['row'] = None

#     if message.data == "si":
#         row['split'] = True 
#     handle_add_row(row, username, chat_id, user_id)

def on_timeout(chat_id: str, user_id: str, username: str, message_id: str):
    with bot.retrieve_data(user_id, chat_id) as data:
        row = data["row"]
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="🤔 Vuoi che questa spesa sia divisa? → ❌ No (Default - timeout)",
        reply_markup=None
    )
    handle_add_row(row, username, chat_id, user_id)

def handle_add_row(row, username, chat_id, user_id):
    cancel_timeout(user_id)
    logger.info("Inizio add_row per utente %s", username)
    add_row(row, username)
    bot.delete_state(user_id, chat_id)
    bot.send_message(chat_id, f"✅ Spesa aggiunta: {row['description']} - {row['price']}€ {'(diviso)' if row['split'] else ''}")

def start_timeout(chat_id, user_id, username, seconds, message_id):
    # Cancella eventuale timer precedente
    cancel_timeout(user_id)

    timer = threading.Timer(seconds, on_timeout, args=[chat_id, user_id, username, message_id])
    timer.start()
    active_timers[user_id] = timer

def cancel_timeout(user_id):
    if user_id in active_timers:
        active_timers[user_id].cancel()
        del active_timers[user_id]
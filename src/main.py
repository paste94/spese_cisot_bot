# """ Main module to start project """

from datetime import datetime
import time

from services.messages.utils import parse_message
from services.users.utils import check_user
from services.utilities import send_upload_document_action, handle_errors
from services.gsheet.utils import get_sheet_name
from services.gsheet.utils import add_row
from services.logger.logger import logger
from bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.users.users import USERS
from collections import defaultdict

user_states = defaultdict(lambda: None)  # None, "waiting_link", "waiting_confirm"

### BUTTONS ###
def add_sheet_button(chat_id: str):
    user_states[chat_id] = "waiting_link"
    bot.send_message(chat_id, '🔗 Inserisci il link del nuovo Google Sheet da usare:')

def set_new_link_button(chat_id: str, username: str, update_current: bool):
    link = user_states[f"{chat_id}_link"]
    USERS.add_url_to_list(username, link, update_current=update_current)
    bot.send_message(chat_id, f'✅ Impostato nuovo sheet{" come default "if update_current else " "}correttamente.')
    user_states[f"{chat_id}_link"] = None
    user_states[chat_id] = None

def switch_index_button(chat_id: str, username: str, index: int):
    USERS.switch_url_by_index(username, index)
    bot.send_message(chat_id, f'✅ Sheet cambiato correttamente.')

### MESSAGE HANDLERS ###
def new_link_handler(message: str):
    link = message.text.strip()
    chat_id = message.chat.id
    user_states[f"{chat_id}_link"] = link

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✅ Sì (Default)", callback_data="si"),
        InlineKeyboardButton("❌ No", callback_data="no")
    )

    sheet_name = get_sheet_name(link)  # Verifica che il link sia valido

    bot.send_message(
        chat_id,
        f"📊 Sheet {sheet_name} trovato: Vuoi che questo sheet diventi il default?",
        reply_markup=markup
    )

    user_states[chat_id] = "waiting_confirm"

def add_row_handler(message):
    row = parse_message(message.text)
    logger.info("Row parsed: %s", row)
    add_row(row, message.from_user.username)
    logger.info("Row added to sheet")
    bot.send_message(message.chat.id, f"✅ Spesa aggiunta: {row['description']} - {row['price']}€ {'(diviso)' if row['split'] else ''}")

# /help
@bot.message_handler(commands=['help'])
@handle_errors
def help_cmd(message):
    check_user(message.from_user)
    logger.info("Help command received from user %s", message.from_user.username)
    bot.send_message(
        message.chat.id,
        """ℹ️ Per aggiungere una spesa, invia un messaggio nel formato:

<prezzo> <descrizione> [diviso]""",
        parse_mode="Markdown"
    )

# /about
@bot.message_handler(commands=['about'])
def about_cmd(message):
    check_user(message.from_user)
    logger.info("About command received from user %s", message.from_user.username)
    bot.send_message(message.chat.id, "🤖 Bot Cisottiano per la gestione delle spese in famiglia. Se non sei un Cisot non dovresti stare qui.")

# /settings
@bot.message_handler(commands=['settings'])
def about_cmd(message):
    check_user(message.from_user)
    logger.info("Settings command received from user %s", message.from_user.username)
    current_url = USERS.get_url(message.from_user.username)
    old_url = USERS.get_old(message.from_user.username)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(f"📊 {get_sheet_name(current_url)} (CURRENT)", callback_data='current'),
    )
    for index, url in enumerate(old_url):
        markup.add(
            InlineKeyboardButton(f"📊 {get_sheet_name(url)}", callback_data=str(index)),
        )
    markup.add(
        InlineKeyboardButton(f"➕ Aggiungi nuovo sheet", callback_data='new'),
    )

    bot.send_message(message.chat.id, "Seleziona uno sheet", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
@handle_errors
def handle_button_click(call):
    check_user(call.from_user)
    logger.info("Button click received from user %s: %s", call.from_user.username, call.data)   
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    if call.data == 'new': 
        add_sheet_button(chat_id)
    if call.data == 'si':
        set_new_link_button(chat_id, call.from_user.username, True)
    if call.data == 'no':
        set_new_link_button(chat_id, call.from_user.username, False)
    if call.data == 'current':
        bot.send_message(chat_id, f"📊 Sheet corrente: {get_sheet_name(USERS.get_url(call.from_user.username))}")
    if call.data.isdigit():
        switch_index_button(chat_id, call.from_user.username, int(call.data))

@bot.message_handler(func=lambda msg: True)
# @handle_errors
# @send_upload_document_action
def get_message(message):
    receive_delay = time.time() - message.date
    logger.info(
        "📥 Messaggio ricevuto da @%s | Ritardo polling: %.2fs",
        message.from_user.username,
        receive_delay
    )
    t0 = time.time()
    bot.send_message(message.chat.id, f"PISELLO: {message.text}")
    t1 = time.time()
    logger.info(
        "📥 Messaggio inoltrato a @%s | Ritardo invio: %.2fs",
        message.from_user.username,
        t1-t0
    )
    # check_user(message.from_user)
    # logger.info("Message received from user %s: \"%s\"", message.from_user.username, message.text)
    # chat_id = message.chat.id
    # if user_states[chat_id] == "waiting_link":
    #     new_link_handler(message)
    # else:
    #     add_row_handler(message)

@bot.message_handler(commands=['about'])
def about_cmd(message):
    check_user(message.from_user)
    logger.info("About command received from user %s", message.from_user.username)
    bot.send_message(message.chat.id, "🤖 Bot di esempio con suggerimenti di interazione.")

if __name__ == '__main__':
    logger.info('Bot started...')
    bot.infinity_polling()
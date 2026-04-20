# """ Main module to start project """

# import logging
# from logging.handlers import TimedRotatingFileHandler

# from bot_instance import bot

# import handlers.about
# import handlers.help
# import handlers.message
# import handlers.settings

# # ── Logging con rotazione giornaliera (max 7 giorni) ─────────
# LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
# LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

# root_logger = logging.getLogger()
# root_logger.setLevel(logging.INFO)

# # File handler: ruota ogni mezzanotte, tiene max 7 file
# file_handler = TimedRotatingFileHandler(
#     filename="bot.log",
#     when="midnight",
#     interval=1,
#     backupCount=7,
#     encoding="utf-8",
# )
# file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FMT))
# root_logger.addHandler(file_handler)

# # Console handler: per journalctl / stdout
# console_handler = logging.StreamHandler()
# console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FMT))
# root_logger.addHandler(console_handler)

# logger = logging.getLogger(__name__)

# if __name__ == '__main__':
#     logger.info('Bot started...')
#     bot.infinity_polling(
#         timeout=20,
#         long_polling_timeout=20,
#         allowed_updates=['message', 'callback_query'],
#     )

#%%
from config import DIV_STRINGS, MONTH_NAMES
import os
import telebot
import gspread
import traceback

from dotenv import load_dotenv
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from functools import wraps
from services.users import Users
from my_exceptions import MessageFormatNotSupported, UnknownLLinkError
from collections import defaultdict
from gspread import NoValidUrlKeyFound

load_dotenv()

USERS=Users()
# GET IT FROM BOTFATHER 
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# GET IT FROM GOOGLE SHEET API
CREDENTIALS_FILE = "g-sheet-credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

user_states = defaultdict(lambda: None)  # None, "waiting_link", "waiting_confirm"

def parse_message(message):
    tokens = message.strip().split(' ', 1)
    try: 
        price = float(tokens[0].replace(',', '.'))
    except ValueError as e:
        if "could not convert string to float" in str(e):
            raise MessageFormatNotSupported(f"Impossibile convertire '{tokens[0].replace(',', '.')}' in numero. Il formato corretto è <NUMERO> <DESCRIZIONE> <Diviso?>") 

    try:
        if tokens[1].lower().endswith(tuple(DIV_STRINGS)):
            split = True
        else:
            split = False
        description = tokens[1].replace('diviso', '').replace(',','').strip()
    except ValueError as e:
        if "list index out of range" in str(e):
            raise MessageFormatNotSupported(f"Descriziona mancante. Il formato corretto è <NUMERO> <DESCRIZIONE> <Diviso?>") 

    row = {
        'price': price,
        'description': description,
        'split': split,
    }
    return row

def handle_errors(bot):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Log completo stacktrace
                error_msg = f"❌ ERRORE in {func.__name__}:\n{str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                
                # Manda messaggio errore all'utente (se disponibile)
                try:
                    if args and hasattr(args[0], 'chat'):
                        chat_id = args[0].chat.id
                        bot.send_message(chat_id, f"❌ Errore interno: {str(e)}")
                except:
                    pass  # Se non riesce a mandare, ignora
                
                return None
        return wrapper
    return decorator

def add_row(row, username: str):
    now = datetime.now()
    month = MONTH_NAMES[now.month]
    # Gets right worksheet

    spreadsheet = CLIENT.open_by_url(USERS.get_url(username))
    sheet = spreadsheet.worksheet(month)

    # Finds the first empty row
    cols = sheet.range(1, 1, sheet.row_count, 1)
    index  = [cell.value for cell in cols].index('')+1

    sheet.update_cell(index, 1, row['description'])
    sheet.update_cell(index, 2, now.day)
    sheet.update_cell(index, 3, row['price'])
    sheet.update_cell(index, 6, row['split'])

def get_sheet_name(url: str) -> str:
    try:
        spreadsheet = CLIENT.open_by_url(url)
        return spreadsheet.title
    except Exception as e:
        if isinstance(e, NoValidUrlKeyFound):
            raise UnknownLLinkError("Link Google Sheet non valido")
        if isinstance(e, PermissionError):
            raise PermissionError("Accesso negato allo Sheet. Per ottenerlo, accedere allo sheet e condividerlo con l'user del bot.")
        raise e


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
    add_row(row, message.from_user.username)
    bot.send_message(message.chat.id, f"✅ Spesa aggiunta: {row['description']} - {row['price']}€ {'(diviso)' if row['split'] else ''}")


#%%

bot = telebot.TeleBot(TOKEN)
bot.set_my_commands([
    telebot.types.BotCommand("help", "🆘 Guida rapida"),
    telebot.types.BotCommand("about", "👀 Info sul bot"),
    telebot.types.BotCommand("settings", "⚙️ Impostazioni"),
])

# /help
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        """ℹ️ Per aggiungere una spesa, invia un messaggio nel formato:

<prezzo> <descrizione> [diviso]""",
        parse_mode="Markdown"
    )

# /about
@bot.message_handler(commands=['about'])
def about_cmd(message):
    bot.send_message(message.chat.id, "🤖 Bot Cisottiano per la gestione delle spese in famiglia. Se non sei un Cisot non dovresti stare qui.")

# /settings
@bot.message_handler(commands=['settings'])
def about_cmd(message):
    if not USERS.is_authorized(message.from_user.username):
        bot.reply_to(message, "❌ Non sei autorizzato a inviare messaggi.")
        return

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
@handle_errors(bot)
def handle_button_click(call):
    if not USERS.is_authorized(call.from_user.username):
        bot.reply_to(call.message, "❌ Non sei autorizzato a inviare messaggi.")
        return
    
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    old_url = USERS.get_old(call.from_user.username)
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
@handle_errors(bot)
def get_message(message):
    if not USERS.is_authorized(message.from_user.username):
        bot.reply_to(message, "❌ Non sei autorizzato a inviare messaggi.")
        return

    chat_id = message.chat.id
    if user_states[chat_id] == "waiting_link":
        new_link_handler(message)
    else:
        add_row_handler(message)

@bot.message_handler(commands=['about'])
def about_cmd(message):
    bot.send_message(message.chat.id, "🤖 Bot di esempio con suggerimenti di interazione.")

bot.infinity_polling()
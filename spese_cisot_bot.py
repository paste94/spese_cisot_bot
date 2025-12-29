#%%
from dotenv import load_dotenv
import os
import telebot
from const import month_name, division_string
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
import gspread
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from functools import wraps
from users.users import Users
import traceback
from my_exceptions import MessageFormatNotSupported

load_dotenv()

USERS=Users()
# GET IT FROM BOTFATHER 
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# GET IT FROM GOOGLE SHEET API
CREDENTIALS_FILE = "g-sheet-credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

def parse_message(message):
    tokens = message.strip().split(' ', 1)
    try: 
        price = float(tokens[0].replace(',', '.'))
    except ValueError as e:
        if "could not convert string to float" in str(e):
            raise MessageFormatNotSupported(f"Impossibile convertire '{tokens[0].replace(',', '.')}' in numero. Il formato corretto è <NUMERO> <DESCRIZIONE> <Diviso?>") 

    try:
        if tokens[1].lower().endswith(tuple(division_string)):
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
    month = month_name[now.month]
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
    spreadsheet = CLIENT.open_by_url(url)
    return spreadsheet.title


#%%

bot = telebot.TeleBot(TOKEN)
bot.set_my_commands([
    telebot.types.BotCommand("help", "Guida rapida"),
    telebot.types.BotCommand("about", "Info sul bot"),
    telebot.types.BotCommand("settings", "Impostazioni"),
])

# /help
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        """Per aggiungere una spesa, invia un messaggio nel formato:

<prezzo> <descrizione> [diviso|divisa|div|splittata|splittato|split]""",
        parse_mode="Markdown"
    )

# /about
@bot.message_handler(commands=['about'])
def about_cmd(message):
    bot.send_message(message.chat.id, "Bot Cisottiano per la gestione delle spese in famiglia. Se non sei un Cisot non dovresti stare qui.")

# /settings
@bot.message_handler(commands=['settings'])
def about_cmd(message):
    if USERS.is_authorized(message.from_user.username):
        current_url = USERS.get_url(message.from_user.username)
        old_url = USERS.get_old(message.from_user.username)
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton(f"{get_sheet_name(current_url)} (CURRENT)", callback_data='current'),
        )
        for index, url in enumerate(old_url):
            markup.add(
                InlineKeyboardButton(f"{get_sheet_name(url)}", callback_data=index),
            )
        markup.add(
            InlineKeyboardButton(f"Aggiungi nuovo sheet", callback_data='new'),
        )

        bot.send_message(message.chat.id, "Seleziona uno sheet", reply_markup=markup)
        
    else:
        bot.reply_to(message, "Non sei autorizzato a stare qui.")
        return

@bot.callback_query_handler(func=lambda call: True)
@handle_errors(bot)
def handle_button_click(call):
    # ✅ IMPORTANTE: Conferma il click
    print(f'BUTTON CLICK {call}')
    bot.answer_callback_query(call.id)
    chat_id = call.message.chat.id
    # message_id = call.message.chat.id
    bot.send_message(call.message.chat.id, call.data)
    if call.data == 'new': 
        bot.send_message(call.message.chat.id, call.data)



@bot.message_handler(func=lambda msg: True)
@handle_errors(bot)
def get_message(message):
    print(f'Message: {message.text}')
    # try:
    if USERS.is_authorized(message.from_user.username):
        row = parse_message(message.text)
        add_row(row, message.from_user.username)
    else:
        bot.reply_to(message, "Non sei autorizzato a inviare spese.")
        return
    bot.send_message(message.chat.id, f"Spesa aggiunta: {row['description']} - {row['price']}€ {'(diviso)' if row['split'] else ''}")

@bot.message_handler(commands=['about'])
def about_cmd(message):
    bot.send_message(message.chat.id, "🤖 Bot di esempio con suggerimenti di interazione.")

bot.infinity_polling()

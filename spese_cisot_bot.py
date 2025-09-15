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

from users.users import Users

load_dotenv()

USERS=Users()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
CREDENTIALS_FILE = "g-sheet-credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)
# SPREADSHEET = CLIENT.open_by_url(USERS.get_url('RicPast'))

def parse_message(message):
    tokens = message.strip().split(' ', 1)
    # print(tokens)
    price = float(tokens[0].replace(',', '.'))

    if tokens[1].lower().endswith(tuple(division_string)):
        split = True
    else:
        split = False
    description = tokens[1]
    for div_string in division_string:
        description = description.replace(div_string, '')
    description = description.replace(',','').strip()
    row = {
        'price': price,
        'description': description,
        'split': split,
    }
    return row
    # print(row)ù

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

#%%

bot = telebot.TeleBot(TOKEN)
bot.set_my_commands([
    telebot.types.BotCommand("help", "Guida rapida"),
    telebot.types.BotCommand("about", "Info sul bot"),
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


@bot.message_handler(func=lambda msg: True)
def get_message(message):
    print(f'Message: {message.text}')
    try:
        if USERS.is_authorized(message.from_user.username):
            try:
                row = parse_message(message.text)
            except Exception as e:
                print(f"Error: {e}")
                bot.reply_to(message, f"Errore nell'elaborazione del messaggio. Assicurati che il formato sia corretto.\n\n{e}")
                return
            add_row(row, message.from_user.username)
        else:
            bot.reply_to(message, "Non sei autorizzato a inviare spese. Solo RicPast può farlo.")
            return
        bot.send_message(message.chat.id, f"Spesa aggiunta: {row['description']} - {row['price']}€ {'(diviso)' if row['split'] else ''}")
    except ValueError as e:
        bot.reply_to(message, e.message)
    # bot.reply_to(message, message.text)

@bot.message_handler(commands=['about'])
def about_cmd(message):
    bot.send_message(message.chat.id, "🤖 Bot di esempio con suggerimenti di interazione.")

bot.infinity_polling()

# %%

#%%
from dotenv import load_dotenv
import os
import telebot
from const import month_name
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
import gspread

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
SHEET_ID = os.getenv("SHEET_ID")
CREDENTIALS_FILE = "g-sheet-credentials.json"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)
SPREADSHEET = CLIENT.open_by_url('https://docs.google.com/spreadsheets/d/1yoxWN_bRS72kvwrgIGEyo-Qq_Mr8oXNNme4FOQjD_hU/edit?gid=94192932#gid=94192932')


def parse_message(message):
    tokens = message.strip().split(' ', 1)
    # print(tokens)
    price = float(tokens[0].replace(',', '.'))
    if 'diviso' in tokens[1]:
        split = True
    else:
        split = False
    description = tokens[1].replace('diviso', '').replace(',','').strip()
    row = {
        'price': price,
        'description': description,
        'split': split,
    }
    return row
    # print(row)ù

def add_row(row):
    now = datetime.now()
    month = month_name[now.month]
    # Gets right worksheet
    sheet = SPREADSHEET.worksheet(month)

    # Finds the first empty row
    cols = sheet.range(1, 1, sheet.row_count, 1)
    index  = [cell.value for cell in cols].index('')+1

    sheet.update_cell(index, 1, row['description'])
    sheet.update_cell(index, 2, now.day)
    sheet.update_cell(index, 3, row['price'])
    sheet.update_cell(index, 6, row['split'])

#%%

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda msg: True)
def get_message(message):
    print(f'Message: {message.text}')
    if(message.from_user.username == 'RicPast'):
        try:
            row = parse_message(message.text)
            add_row(row)
        except Exception as e:
            print(f"Error: {e}")
            bot.reply_to(message, f"Errore nell'elaborazione del messaggio. Assicurati che il formato sia corretto.\n\n{e}")
            return
    else:
        bot.reply_to(message, "Non sei autorizzato a inviare spese. Solo RicPast può farlo.")
        return
    # bot.reply_to(message, message.text)
    bot.send_message(message.chat.id, f"Spesa aggiunta: {row['description']} - {row['price']}€ {'(diviso)' if row['split'] else ''}")

bot.infinity_polling()

# %%

""" Bot instance and Telegram API setup """

import os
from dotenv import load_dotenv
from telebot import TeleBot, types
from telebot.storage import StateMemoryStorage
from requests.adapters import HTTPAdapter
import requests
import telebot.apihelper as apihelper

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# Crea un adapter con MAX 1 connessione nel pool
adapter = HTTPAdapter(pool_connections=1, pool_maxsize=1)

# Applica all'inizio, prima di creare il bot
session = requests.Session()
session.mount('https://', adapter)

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
apihelper.READ_TIMEOUT = 5      # 5s invece di 25s
apihelper.CONNECT_TIMEOUT = 3   # 3s per il connect

state_storage = StateMemoryStorage()
bot = TeleBot(TOKEN, state_storage=state_storage)
bot.set_my_commands([
    types.BotCommand("help", "🆘 Guida rapida"),
    types.BotCommand("about", "👀 Info sul bot"),
    types.BotCommand("settings", "⚙️ Impostazioni"),
])
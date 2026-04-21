""" Bot instance and Telegram API setup """

import os
from dotenv import load_dotenv
from telebot import TeleBot, types
from telebot.storage import StateMemoryStorage
import telebot.apihelper as apihelper
import threading
import time
from services.logger.logger import logger


load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

apihelper.SESSION_TIME_TO_LIVE = 5 * 60  # ricrea la sessione ogni 5 minuti

state_storage = StateMemoryStorage()

def clean_storage():
    try:
        while True:
            time.sleep(3600)  # ogni ora
            state_storage.data.clear()  # svuota tutti gli stati
            logger.info("State storage pulito")
    except Exception as e:
        logger.error("Errore durante la pulizia dello storage: %s", e)


cleaner = threading.Thread(target=clean_storage, daemon=True)
cleaner.start()

bot = TeleBot(TOKEN, state_storage=state_storage)
bot.set_my_commands([
    types.BotCommand("help", "🆘 Guida rapida"),
    types.BotCommand("about", "👀 Info sul bot"),
    types.BotCommand("settings", "⚙️ Impostazioni"),
])
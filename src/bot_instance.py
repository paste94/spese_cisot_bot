""" Bot instance and Telegram API setup """

import os
from dotenv import load_dotenv
from telebot import TeleBot, types
from telebot.storage import StateMemoryStorage
import telebot.apihelper as apihelper

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

apihelper.SESSION_TIME_TO_LIVE = 5 * 60  # ricrea la sessione ogni 5 minuti

state_storage = StateMemoryStorage()
bot = TeleBot(TOKEN, state_storage=state_storage)
bot.set_my_commands([
    types.BotCommand("help", "🆘 Guida rapida"),
    types.BotCommand("about", "👀 Info sul bot"),
    types.BotCommand("settings", "⚙️ Impostazioni"),
])
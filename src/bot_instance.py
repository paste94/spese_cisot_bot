""" Bot instance and Telegram API setup """

import os
from dotenv import load_dotenv
from telebot import TeleBot, types
from telebot.storage import StateMemoryStorage

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
print(TOKEN)

state_storage = StateMemoryStorage()
bot = TeleBot(TOKEN, state_storage=state_storage)
bot.set_my_commands([
    types.BotCommand("help", "🆘 Guida rapida"),
    types.BotCommand("about", "👀 Info sul bot"),
    types.BotCommand("settings", "⚙️ Impostazioni"),
])
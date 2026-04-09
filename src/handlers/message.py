from bot_instance import bot
from services.gsheet.utils import add_row
from services.utilities import handle_errors, parse_message
from services.users.users import USERS

@bot.message_handler(func=lambda msg: True)
@handle_errors(bot)
def get_message(message):
    if not USERS.is_authorized(message.from_user.username):
        bot.reply_to(message, "❌ Non sei autorizzato a inviare messaggi.")
        return

    row = parse_message(message.text)
    add_row(row, message.from_user.username)
    bot.send_message(message.chat.id, f"✅ Spesa aggiunta: {row['description']} - {row['price']}€ {'(diviso)' if row['split'] else ''}")

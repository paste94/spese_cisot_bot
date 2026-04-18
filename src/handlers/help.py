from bot_instance import bot

# /help
@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(
        message.chat.id,
        """ℹ️ Per aggiungere una spesa, invia un messaggio nel formato:

<prezzo> <descrizione> [diviso]""",
        parse_mode="Markdown"
    )
from bot_instance import bot

# /about
@bot.message_handler(commands=['about'])
def about_cmd(message):
    bot.send_message(message.chat.id, "🤖 Bot Cisottiano per la gestione delle spese in famiglia. Se non sei un Cisot non dovresti stare qui.")

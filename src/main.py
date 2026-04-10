""" Main module to start project """

from bot_instance import bot

import handlers.about
import handlers.help
import handlers.message
import handlers.settings

if __name__ == '__main__':
    print('Bot started...')
    bot.infinity_polling()
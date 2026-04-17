""" Main module to start project """

import logging

from bot_instance import bot

import handlers.about
import handlers.help
import handlers.message
import handlers.settings

# ── Logging con timestamp ────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('Bot started...')
    bot.infinity_polling(
        timeout=20,
        long_polling_timeout=20,
        allowed_updates=['message', 'callback_query'],
    )
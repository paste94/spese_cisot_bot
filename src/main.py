""" Main module to start project """

import logging
from logging.handlers import TimedRotatingFileHandler

from bot_instance import bot

import handlers.about
import handlers.help
import handlers.message
import handlers.settings

# ── Logging con rotazione giornaliera (max 7 giorni) ─────────
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FMT = "%Y-%m-%d %H:%M:%S"

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# File handler: ruota ogni mezzanotte, tiene max 7 file
file_handler = TimedRotatingFileHandler(
    filename="bot.log",
    when="midnight",
    interval=1,
    backupCount=7,
    encoding="utf-8",
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FMT))
root_logger.addHandler(file_handler)

# Console handler: per journalctl / stdout
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FMT))
root_logger.addHandler(console_handler)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('Bot started...')
    bot.infinity_polling(
        timeout=20,
        long_polling_timeout=20,
        allowed_updates=['message', 'callback_query'],
    )